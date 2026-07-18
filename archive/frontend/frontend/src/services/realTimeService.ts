import { useState, useEffect } from 'react';

/**
 * Real-time service for handling live updates
 * Implements polling for real-time data updates
 */

interface RealTimeConfig {
  enabled: boolean;
  pollInterval: number; // milliseconds
  retryAttempts: number;
  retryDelay: number; // milliseconds
}

interface Subscription {
  endpoint: string;
  callback: (data: any) => void;
  interval: number;
  lastUpdate: number;
  errorCount: number;
}

class RealTimeService {
  private subscriptions: Map<string, Subscription> = new Map();
  private config: RealTimeConfig = {
    enabled: true,
    pollInterval: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 5000, // 5 seconds
  };
  private online: boolean = true;

  constructor() {
    this.setupNetworkListeners();
    this.initializeDefaultSubscriptions();
  }

  /**
   * Setup network status listeners
   */
  private setupNetworkListeners(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        this.online = true;
        this.resumeAllSubscriptions();
      });

      window.addEventListener('offline', () => {
        this.online = false;
        this.pauseAllSubscriptions();
      });
    }
  }

  /**
   * Initialize default subscriptions for key endpoints
   */
  private initializeDefaultSubscriptions(): void {
    // Dashboard data updates
    this.subscribe('/dashboard', () => {
      // Trigger dashboard refresh
      window.dispatchEvent(new CustomEvent('dashboard-update'));
    }, this.config.pollInterval);

    // Alerts updates
    this.subscribe('/alerts', () => {
      window.dispatchEvent(new CustomEvent('alerts-update'));
    }, this.config.pollInterval / 2); // Check alerts more frequently

    // Market trends updates
    this.subscribe('/market/trends', () => {
      window.dispatchEvent(new CustomEvent('market-update'));
    }, this.config.pollInterval * 2); // Check trends less frequently
  }

  /**
   * Subscribe to real-time updates for an endpoint
   */
  public subscribe(
    endpoint: string,
    callback: (data: any) => void,
    interval: number = this.config.pollInterval
  ): () => void {
    const subscriptionId = `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const subscription: Subscription = {
      endpoint,
      callback,
      interval,
      lastUpdate: Date.now(),
      errorCount: 0,
    };

    this.subscriptions.set(subscriptionId, subscription);

    // Start polling
    this.startPolling(subscriptionId);

    // Return unsubscribe function
    return () => this.unsubscribe(subscriptionId);
  }

  /**
   * Unsubscribe from updates
   */
  private unsubscribe(subscriptionId: string): void {
    const subscription = this.subscriptions.get(subscriptionId);
    if (subscription) {
      clearTimeout((subscription as any).timeoutId);
      this.subscriptions.delete(subscriptionId);
    }
  }

  /**
   * Start polling for a subscription
   */
  private startPolling(subscriptionId: string): void {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) return;

    if (!this.online || !this.config.enabled) {
      // Retry later
      const timeoutId = setTimeout(
        () => this.startPolling(subscriptionId),
        this.config.retryDelay
      );
      (subscription as any).timeoutId = timeoutId;
      return;
    }

    this.fetchUpdate(subscription)
      .then(() => {
        subscription.errorCount = 0;
        subscription.lastUpdate = Date.now();
        
        // Schedule next poll
        const timeoutId = setTimeout(
          () => this.startPolling(subscriptionId),
          subscription.interval
        );
        (subscription as any).timeoutId = timeoutId;
      })
      .catch((error) => {
        console.error(`Error polling ${subscription.endpoint}:`, error);
        subscription.errorCount++;

        if (subscription.errorCount < this.config.retryAttempts) {
          // Retry with exponential backoff
          const backoffDelay = this.config.retryDelay * Math.pow(2, subscription.errorCount);
          const timeoutId = setTimeout(
            () => this.startPolling(subscriptionId),
            backoffDelay
          );
          (subscription as any).timeoutId = timeoutId;
        } else {
          console.error(`Max retry attempts reached for ${subscription.endpoint}`);
          // Reset error count and try again after longer delay
          subscription.errorCount = 0;
          const timeoutId = setTimeout(
            () => this.startPolling(subscriptionId),
            subscription.interval * 5
          );
          (subscription as any).timeoutId = timeoutId;
        }
      });
  }

  /**
   * Fetch update for a subscription
   */
  private async fetchUpdate(subscription: Subscription): Promise<void> {
    const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1${subscription.endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      subscription.callback(data);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Pause all subscriptions when offline
   */
  private pauseAllSubscriptions(): void {
    this.subscriptions.forEach((subscription, subscriptionId) => {
      clearTimeout((subscription as any).timeoutId);
    });
  }

  /**
   * Resume all subscriptions when back online
   */
  private resumeAllSubscriptions(): void {
    this.subscriptions.forEach((subscription, subscriptionId) => {
      this.startPolling(subscriptionId);
    });
  }

  /**
   * Update configuration
   */
  public updateConfig(newConfig: Partial<RealTimeConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get current status
   */
  public getStatus(): {
    online: boolean;
    enabled: boolean;
    subscriptionCount: number;
    config: RealTimeConfig;
  } {
    return {
      online: this.online,
      enabled: this.config.enabled,
      subscriptionCount: this.subscriptions.size,
      config: this.config,
    };
  }

  /**
   * Clear all subscriptions
   */
  public clearAll(): void {
    this.subscriptions.forEach((_, subscriptionId) => {
      this.unsubscribe(subscriptionId);
    });
    this.subscriptions.clear();
  }
}

// Export singleton instance
export const realTimeService = new RealTimeService();

// Export event names for use in components
export const REAL_TIME_EVENTS = {
  DASHBOARD_UPDATE: 'dashboard-update',
  ALERTS_UPDATE: 'alerts-update',
  MARKET_UPDATE: 'market-update',
  COMPETITOR_UPDATE: 'competitor-update',
  REPORT_UPDATE: 'report-update',
};

// React hook for using real-time updates
export function useRealTimeUpdates() {
  const [isOnline, setIsOnline] = useState(true);
  const [subscriptionCount, setSubscriptionCount] = useState(0);

  useEffect(() => {
    const updateStatus = () => {
      const status = realTimeService.getStatus();
      setIsOnline(status.online);
      setSubscriptionCount(status.subscriptionCount);
    };

    // Update status every second
    const interval = setInterval(updateStatus, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    isOnline,
    subscriptionCount,
    subscribe: realTimeService.subscribe.bind(realTimeService),
    updateConfig: realTimeService.updateConfig.bind(realTimeService),
    clearAll: realTimeService.clearAll.bind(realTimeService),
  };
}