import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { toast } from 'react-toastify';
import { PlusIcon, TrashIcon } from 'lucide-react';

// Components
import BasketItem from '../components/BasketItem';
import PredictionResults from '../components/PredictionResults';
import PredictionHistory from '../components/PredictionHistory';
import ItemSelector from '../components/ItemSelector';

// Services
import * as predictionService from '../services/predictionService';

// Types
import { Prediction, PredictionItem } from '../types';

const PredictionPage: React.FC = () => {
  const [basketItems, setBasketItems] = useState<string[]>([]);
  const [newItem, setNewItem] = useState<string>('');
  const [predictionResults, setPredictionResults] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]); // ✅ history state

  const predictMutation = useMutation(
    (items: string[]) => predictionService.predictNextItem(items),
    {
      onSuccess: (data) => {
        setPredictionResults(data);
        setHistory((prev) => [data, ...prev]); // ✅ Add to history
        toast.success('Prediction complete!');
      },
      onError: (error: any) => {
        toast.error(`Prediction failed: ${error.message || 'Unknown error'}`);
      },
    }
  );

  const handleAddItem = () => {
    if (newItem.trim() === '') return;
    setBasketItems([...basketItems, newItem.trim()]);
    setNewItem('');
  };

  const handleRemoveItem = (index: number) => {
    const updatedItems = [...basketItems];
    updatedItems.splice(index, 1);
    setBasketItems(updatedItems);
  };

  const handlePredict = () => {
    if (basketItems.length === 0) {
      toast.warning('Please add at least one item to your basket');
      return;
    }
    predictMutation.mutate(basketItems);
  };

  const handleClearBasket = () => {
    setBasketItems([]);
    setPredictionResults(null);
  };

  const handleAddPredictedItem = (item: string) => {
    setBasketItems([...basketItems, item]);
    setPredictionResults(null);
  };

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-2xl font-bold mb-6">Smart Basket Predictions</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Current Basket Section */}
        <div className="col-span-1 md:col-span-2 bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Current Basket</h2>
            {basketItems.length > 0 && (
              <button
                onClick={handleClearBasket}
                className="text-red-600 hover:text-red-800 flex items-center"
              >
                <TrashIcon size={16} className="mr-1" />
                Clear
              </button>
            )}
          </div>

          {/* Item Input */}
          <div className="flex mb-4">
            <ItemSelector value={newItem} onChange={setNewItem} />
            <button
              onClick={handleAddItem}
              className="ml-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded flex items-center"
            >
              <PlusIcon size={16} className="mr-1" />
              Add
            </button>
          </div>

          {/* Basket Items */}
          <div className="mb-6">
            {basketItems.length === 0 ? (
              <p className="text-gray-500 italic">Your basket is empty</p>
            ) : (
              <ul className="space-y-2">
                {basketItems.map((item, index) => (
                  <BasketItem
                    key={index}
                    item={item}
                    onRemove={() => handleRemoveItem(index)}
                  />
                ))}
              </ul>
            )}
          </div>

          {/* Predict Button */}
          <button
            onClick={handlePredict}
            disabled={basketItems.length === 0 || predictMutation.isLoading}
            className="w-full bg-green-500 hover:bg-green-600 text-white py-2 rounded font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {predictMutation.isLoading ? 'Predicting...' : 'Predict Next Item'}
          </button>

          {/* Prediction Results */}
          {predictionResults && (
            <PredictionResults
              prediction={predictionResults}
              onAddItem={handleAddPredictedItem}
            />
          )}
        </div>

        {/* Prediction History Section */}
        <div className="col-span-1 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Predictions</h2>
          <PredictionHistory history={history} />
        </div>
      </div>
    </div>
  );
};

export default PredictionPage;
