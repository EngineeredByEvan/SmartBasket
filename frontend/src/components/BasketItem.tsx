import React from 'react';
import { TrashIcon } from 'lucide-react';

interface BasketItemProps {
  item: string;
  onRemove: (item: string) => void;
}

const BasketItem: React.FC<BasketItemProps> = ({ item, onRemove }) => {
  return (
    <div className="flex items-center justify-between p-2 rounded-md bg-white border shadow-sm hover:shadow-md transition">
      <span className="text-sm font-medium text-gray-800">{item}</span>
      <button
        onClick={() => onRemove(item)}
        className="text-red-500 hover:text-red-700"
        title="Remove item"
      >
        <TrashIcon size={16} />
      </button>
    </div>
  );
};

export default BasketItem;
