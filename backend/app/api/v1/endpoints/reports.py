"""
Report generation and management endpoints with file export support.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json
import io
import csv

from app.db.session import get_db
from app.models.alert import Report
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()
logger = get_logger(__name__)


# Pydantic models for request/response
class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: str
    format: str = "pdf"  # pdf, excel, csv
    parameters: Optional[dict] = None


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    parameters: Optional[dict] = None


@router.get("")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List reports with filtering and pagination.
    """
    query = select(Report).where(Report.user_id == current_user.id)
    
    if report_type:
        query = query.where(Report.report_type == report_type)
    
    if status:
        query = query.where(Report.status == status)
    
    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return {
        "reports": [
            {
                "id": report.id,
                "user_id": report.user_id,
                "title": report.title,
                "description": report.description,
                "report_type": report.report_type,
                "format": report.export_formats[0] if report.export_formats else "json",
                "status": report.status,
                "file_size": _format_file_size(report.meta_data.get("file_size", 0)),
                "created_at": report.created_at,
                "generated_at": report.generated_at,
            }
            for report in reports
        ],
        "total": len(reports),
        "skip": skip,
        "limit": limit,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new report.
    """
    report = Report(
        user_id=current_user.id,
        title=report_data.title,
        description=report_data.description,
        report_type=report_data.report_type,
        export_formats=[report_data.format],
        parameters=report_data.parameters or {},
        status="draft",
        is_public=False,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"New report created: {report.title}")
    
    return {
        "id": report.id,
        "message": "Report created successfully",
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new report with the specified format.
    """
    # Create report record
    report = Report(
        user_id=current_user.id,
        title=report_data.title,
        description=report_data.description,
        report_type=report_data.report_type,
        export_formats=[report_data.format],
        parameters=report_data.parameters or {},
        status="generating",
        is_public=False,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"Report generation started: {report.title} (format: {report_data.format})")
    
    # Generate report content
    try:
        content = await _generate_report_content(report_data.report_type, report_data.parameters)
        
        # Generate file based on format
        file_content, file_size, file_extension = await _generate_file(
            content, 
            report_data.format, 
            report_data.title
        )
        
        # Update report with generated content
        report.content = content
        report.status = "ready"
        report.generated_at = datetime.utcnow()
        report.export_paths = [f"report_{report.id}.{file_extension}"]
        report.meta_data = {"file_size": file_size, "format": report_data.format}
        
        await db.commit()
        await db.refresh(report)
        
        logger.info(f"Report generated successfully: {report.title}")
        
        return {
            "id": report.id,
            "title": report.title,
            "status": report.status,
            "format": report_data.format,
            "file_size": _format_file_size(file_size),
            "message": "Report generated successfully",
            "download_url": f"/api/v1/reports/{report.id}/download",
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {report.title} - {str(e)}")
        report.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a report file in the specified format.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready for download (status: {report.status})"
        )
    
    # Get format from export formats
    format_type = report.export_formats[0] if report.export_formats else "json"
    
    # Generate file content
    file_content, file_size, file_extension = await _generate_file(
        report.content or {},
        format_type,
        report.title
    )
    
    # Set appropriate content type
    content_types = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "json": "application/json",
    }
    
    content_type = content_types.get(format_type, "application/octet-stream")
    filename = f"{report.title.replace(' ', '_')}.{file_extension}"
    
    # Create streaming response
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_size),
        }
    )


@router.put("/{report_id}")
async def update_report(
    report_id: int,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing report.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update fields that are provided
    if report_update.title is not None:
        report.title = report_update.title
    if report_update.description is not None:
        report.description = report_update.description
    if report_update.status is not None:
        report.status = report_update.status
    if report_update.parameters is not None:
        report.parameters = report_update.parameters
    
    report.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"Report updated: {report.title}")
    
    return {
        "id": report.id,
        "message": "Report updated successfully",
    }


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a report.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    await db.delete(report)
    await db.commit()
    
    logger.info(f"Report deleted: {report.title}")
    
    return {"message": "Report deleted successfully"}


# Helper functions
async def _generate_report_content(report_type: str, parameters: dict) -> dict:
    """
    Generate report content based on report type and parameters.
    """
    # Sample report content generation
    from datetime import datetime, timedelta
    
    current_date = datetime.now()
    
    if report_type == "competitor":
        return {
            "title": "Competitor Analysis Report",
            "generated_at": current_date.isoformat(),
            "report_type": "competitor",
            "summary": "Comprehensive analysis of top competitors in the market",
            "sections": [
                {
                    "title": "Competitor Overview",
                    "content": [
                        {"competitor": "TechCorp Industries", "market_share": "35%", "growth_rate": "+15%"},
                        {"competitor": "DataFlow Systems", "market_share": "25%", "growth_rate": "+8%"},
                        {"competitor": "CloudNine Solutions", "market_share": "20%", "growth_rate": "+12%"},
                    ]
                },
                {
                    "title": "Market Positioning",
                    "content": [
                        {"metric": "Brand Recognition", "value": "8.5/10"},
                        {"metric": "Customer Satisfaction", "value": "4.2/5"},
                        {"metric": "Price Competitiveness", "value": "3.8/5"},
                    ]
                },
                {
                    "title": "Key Findings",
                    "content": [
                        "TechCorp maintains market leadership through innovation",
                        "DataFlow shows strong customer retention rates",
                        "CloudNine experiencing rapid growth in enterprise segment",
                    ]
                }
            ],
            "recommendations": [
                "Focus on product differentiation",
                "Enhance customer support services",
                "Develop enterprise-specific solutions",
            ]
        }
    
    elif report_type == "market":
        return {
            "title": "Market Intelligence Report",
            "generated_at": current_date.isoformat(),
            "report_type": "market",
            "summary": "Analysis of current market trends and future projections",
            "sections": [
                {
                    "title": "Market Overview",
                    "content": [
                        {"metric": "Total Market Size", "value": "$45B", "growth": "+12% YoY"},
                        {"metric": "Projected Growth", "value": "$65B", "by_year": "2026"},
                        {"metric": "Key Segments", "value": "Enterprise, SMB, Government"},
                    ]
                },
                {
                    "title": "Trend Analysis",
                    "content": [
                        {"trend": "AI Platform Adoption", "impact": "High", "growth": "+35%"},
                        {"trend": "Cloud Migration", "impact": "Medium", "growth": "+45%"},
                        {"trend": "Data Privacy", "impact": "High", "growth": "+25%"},
                    ]
                },
                {
                    "title": "Opportunities",
                    "content": [
                        "Enterprise AI solutions market",
                        "Regulatory compliance tools",
                        "Data analytics platforms",
                    ]
                }
            ],
            "recommendations": [
                "Invest in AI capabilities",
                "Expand cloud offerings",
                "Address data privacy concerns",
            ]
        }
    
    elif report_type == "analytics":
        return {
            "title": "Performance Analytics Report",
            "generated_at": current_date.isoformat(),
            "report_type": "analytics",
            "summary": "Detailed performance metrics and analytics",
            "sections": [
                {
                    "title": "Key Metrics",
                    "content": [
                        {"metric": "Total Competitors Tracked", "value": "24"},
                        {"metric": "Alerts Generated", "value": "156"},
                        {"metric": "Reports Created", "value": "12"},
                        {"metric": "Data Points Collected", "value": "8,432"},
                    ]
                },
                {
                    "title": "Competitor Performance",
                    "content": [
                        {"competitor": "TechCorp", "score": 8.5, "trend": "+0.3"},
                        {"competitor": "DataFlow", "score": 7.2, "trend": "-0.1"},
                        {"competitor": "CloudNine", "score": 7.8, "trend": "+0.2"},
                    ]
                },
                {
                    "title": "Insights",
                    "content": [
                        "TechCorp showing consistent upward trajectory",
                        "DataFlow experiencing slight decline",
                        "CloudNine demonstrating strong growth momentum",
                    ]
                }
            ],
            "recommendations": [
                "Monitor TechCorp closely for competitive threats",
                "Analyze DataFlow's recent decline",
                "Consider partnership opportunities with CloudNine",
            ]
        }
    
    else:  # custom
        return {
            "title": "Custom Report",
            "generated_at": current_date.isoformat(),
            "report_type": "custom",
            "summary": "Custom analysis report based on specified parameters",
            "sections": [
                {
                    "title": "Analysis Results",
                    "content": parameters.get("custom_data", [])
                }
            ],
            "recommendations": parameters.get("recommendations", [])
        }


async def _generate_file(content: dict, format_type: str, title: str) -> tuple[bytes, int, str]:
    """
    Generate file content in the specified format.
    
    Returns: (file_content, file_size, file_extension)
    """
    if format_type == "pdf":
        # Simple PDF-like text representation (in production, use proper PDF library)
        text_content = f"""
        =========================================
        {title}
        =========================================
        
        Generated: {content.get('generated_at', 'N/A')}
        Summary: {content.get('summary', 'N/A')}
        
        """
        
        for section in content.get('sections', []):
            text_content += f"\n{section['title']}\n"
            text_content += "-" * len(section['title']) + "\n"
            
            for item in section.get('content', []):
                if isinstance(item, dict):
                    for key, value in item.items():
                        text_content += f"{key}: {value}\n"
                else:
                    text_content += f"- {item}\n"
            text_content += "\n"
        
        text_content += "\nRecommendations:\n"
        text_content += "-" * 15 + "\n"
        for rec in content.get('recommendations', []):
            text_content += f"- {rec}\n"
        
        file_content = text_content.encode('utf-8')
        return file_content, len(file_content), 'txt'
    
    elif format_type == "csv":
        # Generate CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write summary
        writer.writerow(['Report Title', title])
        writer.writerow(['Generated', content.get('generated_at', 'N/A')])
        writer.writerow(['Summary', content.get('summary', 'N/A')])
        writer.writerow([])
        
        # Write sections
        for section in content.get('sections', []):
            writer.writerow([section['title']])
            writer.writerow([])
            
            # Write headers if content is list of dicts
            if section.get('content') and isinstance(section['content'][0], dict):
                headers = list(section['content'][0].keys())
                writer.writerow(headers)
                
                for item in section['content']:
                    row = [str(item.get(h, '')) for h in headers]
                    writer.writerow(row)
            else:
                for item in section.get('content', []):
                    if isinstance(item, dict):
                        for key, value in item.items():
                            writer.writerow([key, value])
                    else:
                        writer.writerow([item])
            
            writer.writerow([])
        
        # Write recommendations
        writer.writerow(['Recommendations'])
        for rec in content.get('recommendations', []):
            writer.writerow([rec])
        
        csv_content = output.getvalue()
        file_content = csv_content.encode('utf-8')
        return file_content, len(file_content), 'csv'
    
    elif format_type == "excel":
        # Simple Excel-like text representation (in production, use openpyxl)
        text_content = f"Excel Report: {title}\n\n"
        
        for section in content.get('sections', []):
            text_content += f"{section['title']}\n"
            
            if section.get('content') and isinstance(section['content'][0], dict):
                # Table-like format
                headers = list(section['content'][0].keys())
                text_content += "\t".join(headers) + "\n"
                
                for item in section['content']:
                    row = [str(item.get(h, '')) for h in headers]
                    text_content += "\t".join(row) + "\n"
            else:
                for item in section.get('content', []):
                    text_content += str(item) + "\n"
            
            text_content += "\n"
        
        file_content = text_content.encode('utf-8')
        return file_content, len(file_content), 'txt'
    
    else:  # json
        json_content = json.dumps(content, indent=2, ensure_ascii=False)
        file_content = json_content.encode('utf-8')
        return file_content, len(file_content), 'json'


def _format_file_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"