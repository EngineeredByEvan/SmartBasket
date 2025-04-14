import React from 'react';
import { Prediction } from '../types';

interface PredictionHistoryProps {
  history: Prediction[];
}

const PredictionHistory: React.FC<PredictionHistoryProps> = ({ history }) => {
  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-3">Prediction History</h2>
      <ul className="space-y-3">
        {history.map((entry, idx) => (
          <li key={idx} className="p-3 bg-white border rounded-md shadow-sm">
            <div className="text-sm text-gray-600 mb-1">
              <strong>Basket:</strong> {entry.basket.join(', ')}
            </div>
            <div className="text-sm text-gray-800">
              <strong>Predicted:</strong>{' '}
              {entry.predicted_items.map((item) => item.item).join(', ')}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {new Date(entry.timestamp).toLocaleString()}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PredictionHistory;
