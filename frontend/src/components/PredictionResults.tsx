import React from 'react';
import { PlusCircleIcon } from 'lucide-react';
import { Prediction } from '../types';

interface PredictionResultsProps {
  prediction: Prediction;
  onAddItem: (item: string) => void;
}

const PredictionResults: React.FC<PredictionResultsProps> = ({ prediction, onAddItem }) => {
  return (
    <div className="mt-6 border-t pt-4">
      <h3 className="text-lg font-semibold mb-3">Predicted Next Items</h3>
      
      <div className="space-y-3">
        {prediction.predicted_items.map((item, index) => (
          <div 
            key={index}
            className={`flex items-center justify-between p-3 rounded-lg border ${
              index === 0 ? 'bg-green-50 border-green-200' : 'bg-gray-50'
            }`}
          >
            <div className="flex-1">
              <div className="flex justify-between">
                <span className="font-medium">{item.item}</span>
                <span className="text-gray-600 text-sm">
                  {item.probability.toFixed(1)}% confidence
                </span>
              </div>
              
              {/* Progress bar */}
              <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${Math.min(item.probability, 100)}%` }}
                />
              </div>
            </div>
            
            <button
              onClick={() => onAddItem(item.item)}
              className="ml-3 text-blue-600 hover:text-blue-800"
              title="Add to basket"
            >
              <PlusCircleIcon size={20} />
            </button>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-xs text-gray-500">
        Prediction generated at {new Date(prediction.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default PredictionResults;