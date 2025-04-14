import React from 'react';

interface ItemSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const ItemSelector: React.FC<ItemSelectorProps> = ({ value, onChange }) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Enter or select an item"
      className="p-2 border rounded-md w-full"
    />
  );
};

export default ItemSelector;
