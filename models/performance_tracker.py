import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import threading

class PerformanceTracker:
    """Track performance metrics for the resume parser system"""
    
    def __init__(self):
        self.metrics_file = Path("data/metrics/performance_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory metrics storage
        self.metrics = {
            'api_requests': [],
            'model_performance': defaultdict(list),
            'validation_stats': defaultdict(int),
            'company_matching_stats': defaultdict(list),
            'processing_times': defaultdict(list),
            'error_count': 0,
            'total_requests': 0,
            'successful_requests': 0
        }
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Load existing metrics if available
        self.load_metrics()
    
    def load_metrics(self):
        """Load metrics from disk"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    saved = json.load(f)
                    # Convert defaultdict back
                    for key in ['model_performance', 'validation_stats', 
                               'company_matching_stats', 'processing_times']:
                        if key in saved:
                            self.metrics[key] = defaultdict(list, saved[key])
                    # Update scalars
                    for key in ['error_count', 'total_requests', 'successful_requests']:
                        if key in saved:
                            self.metrics[key] = saved[key]
            except Exception as e:
                print(f"Could not load metrics: {e}")
    
    def save_metrics(self):
        """Persist metrics to disk"""
        with self.lock:
            try:
                # Convert defaultdict to regular dict for JSON serialization
                save_data = {
                    'api_requests': self.metrics['api_requests'][-1000:],  # Keep last 1000
                    'model_performance': dict(self.metrics['model_performance']),
                    'validation_stats': dict(self.metrics['validation_stats']),
                    'company_matching_stats': dict(self.metrics['company_matching_stats']),
                    'processing_times': dict(self.metrics['processing_times']),
                    'error_count': self.metrics['error_count'],
                    'total_requests': self.metrics['total_requests'],
                    'successful_requests': self.metrics['successful_requests'],
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(self.metrics_file, 'w') as f:
                    json.dump(save_data, f, indent=2)
            except Exception as e:
                print(f"Could not save metrics: {e}")
    
    def track_request(self, endpoint: str, duration: float, status: str, 
                     details: Dict = None):
        """Track API request metrics"""
        with self.lock:
            self.metrics['total_requests'] += 1
            if status == 'success':
                self.metrics['successful_requests'] += 1
            elif status == 'error':
                self.metrics['error_count'] += 1
            
            request_data = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'duration_ms': round(duration * 1000, 2),
                'status': status
            }
            
            if details:
                request_data.update(details)
            
            self.metrics['api_requests'].append(request_data)
            self.metrics['processing_times'][endpoint].append(duration)
    
    def track_validation(self, is_valid: bool, confidence: float):
        """Track resume validation metrics"""
        with self.lock:
            if is_valid:
                self.metrics['validation_stats']['valid_resumes'] += 1
            else:
                self.metrics['validation_stats']['invalid_resumes'] += 1
            
            self.metrics['validation_stats']['total_validations'] += 1
            self.metrics['validation_stats']['confidence_scores'] = \
                self.metrics['validation_stats'].get('confidence_scores', []) + [confidence]
    
    def track_ml_prediction(self, model_name: str, confidence: float, 
                          prediction_time: float):
        """Track ML model performance"""
        with self.lock:
            self.metrics['model_performance'][model_name].append({
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence,
                'prediction_time_ms': round(prediction_time * 1000, 2)
            })
    
    def track_company_matching(self, num_companies: int, avg_match_score: float,
                              processing_time: float):
        """Track company matching performance"""
        with self.lock:
            self.metrics['company_matching_stats']['total_matches'].append({
                'timestamp': datetime.now().isoformat(),
                'num_companies': num_companies,
                'avg_match_score': round(avg_match_score, 2),
                'processing_time_ms': round(processing_time * 1000, 2)
            })
    
    def get_statistics(self) -> Dict:
        """Get aggregated statistics"""
        with self.lock:
            stats = {
                'total_requests': self.metrics['total_requests'],
                'successful_requests': self.metrics['successful_requests'],
                'error_count': self.metrics['error_count'],
                'success_rate': round(
                    (self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)) * 100, 
                    2
                ),
                'validation_stats': dict(self.metrics['validation_stats']),
                'model_performance': {},
                'avg_processing_times': {}
            }
            
            # Calculate average processing times
            for endpoint, times in self.metrics['processing_times'].items():
                if times:
                    stats['avg_processing_times'][endpoint] = {
                        'avg_ms': round(sum(times) / len(times) * 1000, 2),
                        'min_ms': round(min(times) * 1000, 2),
                        'max_ms': round(max(times) * 1000, 2),
                        'count': len(times)
                    }
            
            # Model performance summary
            for model, predictions in self.metrics['model_performance'].items():
                if predictions:
                    confidences = [p['confidence'] for p in predictions]
                    times = [p['prediction_time_ms'] for p in predictions]
                    stats['model_performance'][model] = {
                        'total_predictions': len(predictions),
                        'avg_confidence': round(sum(confidences) / len(confidences), 2),
                        'avg_time_ms': round(sum(times) / len(times), 2)
                    }
            
            return stats

# Global tracker instance
performance_tracker = PerformanceTracker()
