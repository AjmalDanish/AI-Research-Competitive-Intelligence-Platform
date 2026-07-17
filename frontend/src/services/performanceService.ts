import { useState } from 'react';

/**
 * Performance optimization utilities
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

class CacheService {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private defaultExpiry = 5 * 60 * 1000; // 5 minutes

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiry) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, expiry?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      expiry: Date.now() + (expiry || this.defaultExpiry),
    };
    this.cache.set(key, entry);
  }

  /**
   * Clear specific cache entry
   */
  clear(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Clear all cache
   */
  clearAll(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number;
    keys: string[];
    oldestEntry: number | null;
    newestEntry: number | null;
  } {
    const entries = Array.from(this.cache.values());
    const timestamps = entries.map(e => e.timestamp);

    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      oldestEntry: timestamps.length > 0 ? Math.min(...timestamps) : null,
      newestEntry: timestamps.length > 0 ? Math.max(...timestamps) : null,
    };
  }
}

class DebounceService {
  private timers: Map<string, NodeJS.Timeout> = new Map();

  /**
   * Debounce function execution
   */
  debounce<T extends (...args: any[]) => any>(
    key: string,
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    return (...args: Parameters<T>) => {
      if (this.timers.has(key)) {
        clearTimeout(this.timers.get(key)!);
      }

      this.timers.set(
        key,
        setTimeout(() => {
          func(...args);
          this.timers.delete(key);
        }, delay)
      );
    };
  }

  /**
   * Cancel pending debounced execution
   */
  cancel(key: string): void {
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key)!);
      this.timers.delete(key);
    }
  }

  /**
   * Clear all pending debounces
   */
  clearAll(): void {
    this.timers.forEach((timer) => clearTimeout(timer));
    this.timers.clear();
  }
}

class ThrottleService {
  private lastExecutions: Map<string, number> = new Map();

  /**
   * Throttle function execution
   */
  throttle<T extends (...args: any[]) => any>(
    key: string,
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    return (...args: Parameters<T>) => {
      const now = Date.now();
      const lastExecution = this.lastExecutions.get(key) || 0;

      if (now - lastExecution >= limit) {
        func(...args);
        this.lastExecutions.set(key, now);
      }
    };
  }

  /**
   * Clear throttle history
   */
  clear(key: string): void {
    this.lastExecutions.delete(key);
  }

  /**
   * Clear all throttle history
   */
  clearAll(): void {
    this.lastExecutions.clear();
  }
}

class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();
  private maxSamples = 100;

  /**
   * Measure function execution time
   */
  async measure<T>(key: string, func: () => Promise<T>): Promise<T> {
    const start = performance.now();
    try {
      const result = await func();
      const duration = performance.now() - start;
      this.recordMetric(key, duration);
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      this.recordMetric(key, duration, true);
      throw error;
    }
  }

  /**
   * Record a metric
   */
  recordMetric(key: string, value: number, isError: boolean = false): void {
    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }

    const samples = this.metrics.get(key)!;
    samples.push(value);

    // Keep only the most recent samples
    if (samples.length > this.maxSamples) {
      samples.shift();
    }
  }

  /**
   * Get metrics for a key
   */
  getMetrics(key: string): {
    count: number;
    min: number;
    max: number;
    avg: number;
    median: number;
    p95: number;
    p99: number;
  } | null {
    const samples = this.metrics.get(key);
    if (!samples || samples.length === 0) return null;

    const sorted = [...samples].sort((a, b) => a - b);
    const sum = samples.reduce((a, b) => a + b, 0);

    return {
      count: samples.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      avg: sum / samples.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
    };
  }

  /**
   * Clear metrics for a key
   */
  clearMetrics(key: string): void {
    this.metrics.delete(key);
  }

  /**
   * Clear all metrics
   */
  clearAllMetrics(): void {
    this.metrics.clear();
  }

  /**
   * Get all metric keys
   */
  getMetricKeys(): string[] {
    return Array.from(this.metrics.keys());
  }
}

class ResourceOptimizer {
  private imageCache: Map<string, HTMLImageElement> = new Map();
  private requestQueue: Map<string, Promise<any>> = new Map();

  /**
   * Optimize image loading with caching
   */
  async loadImage(src: string): Promise<HTMLImageElement> {
    if (this.imageCache.has(src)) {
      return this.imageCache.get(src)!;
    }

    if (this.requestQueue.has(src)) {
      return this.requestQueue.get(src)!;
    }

    const promise = new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.imageCache.set(src, img);
        this.requestQueue.delete(src);
        resolve(img);
      };
      img.onerror = () => {
        this.requestQueue.delete(src);
        reject(new Error(`Failed to load image: ${src}`));
      };
      img.src = src;
    });

    this.requestQueue.set(src, promise);
    return promise;
  }

  /**
   * Clear image cache
   */
  clearImageCache(): void {
    this.imageCache.clear();
  }

  /**
   * Clear request queue
   */
  clearRequestQueue(): void {
    this.requestQueue.clear();
  }

  /**
   * Lazy load images when they come into viewport
   */
  observeImages(options: IntersectionObserverInit = {}): IntersectionObserver {
    return new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
        }
      });
    }, {
      rootMargin: '50px',
      threshold: 0.1,
      ...options,
    });
  }

  /**
   * Batch DOM updates for better performance
   */
  batchUpdates(updates: (() => void)[]): void {
    requestAnimationFrame(() => {
      updates.forEach(update => update());
    });
  }
}

// Export singleton instances
export const cacheService = new CacheService();
export const debounceService = new DebounceService();
export const throttleService = new ThrottleService();
export const performanceMonitor = new PerformanceMonitor();
export const resourceOptimizer = new ResourceOptimizer();

// React hooks for performance optimization
export function useCache() {
  return {
    get: cacheService.get.bind(cacheService),
    set: cacheService.set.bind(cacheService),
    clear: cacheService.clear.bind(cacheService),
    clearAll: cacheService.clearAll.bind(cacheService),
    getStats: cacheService.getStats.bind(cacheService),
  };
}

export function useDebounce() {
  return {
    debounce: debounceService.debounce.bind(debounceService),
    cancel: debounceService.cancel.bind(debounceService),
    clearAll: debounceService.clearAll.bind(debounceService),
  };
}

export function useThrottle() {
  return {
    throttle: throttleService.throttle.bind(throttleService),
    clear: throttleService.clear.bind(throttleService),
    clearAll: throttleService.clearAll.bind(throttleService),
  };
}

export function usePerformance() {
  return {
    measure: performanceMonitor.measure.bind(performanceMonitor),
    getMetrics: performanceMonitor.getMetrics.bind(performanceMonitor),
    clearMetrics: performanceMonitor.clearMetrics.bind(performanceMonitor),
    clearAllMetrics: performanceMonitor.clearAllMetrics.bind(performanceMonitor),
    getMetricKeys: performanceMonitor.getMetricKeys.bind(performanceMonitor),
  };
}

export function useResourceOptimization() {
  return {
    loadImage: resourceOptimizer.loadImage.bind(resourceOptimizer),
    observeImages: resourceOptimizer.observeImages.bind(resourceOptimizer),
    batchUpdates: resourceOptimizer.batchUpdates.bind(resourceOptimizer),
    clearImageCache: resourceOptimizer.clearImageCache.bind(resourceOptimizer),
    clearRequestQueue: resourceOptimizer.clearRequestQueue.bind(resourceOptimizer),
  };
}