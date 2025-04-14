import React, { useEffect, useState } from 'react';
import { Transaction } from '../types';
import * as transactionService from '../services/transactionService';

const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const data = await transactionService.getTransactions();
        setTransactions(data);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    };

    fetchTransactions();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Your Transactions</h1>
      <div className="space-y-4">
        {transactions.map((tx) => (
          <div key={tx.id} className="p-4 bg-white border rounded shadow-sm">
            <div className="text-sm text-gray-800">
              <strong>Date:</strong> {new Date(tx.date).toLocaleDateString()}
            </div>
            <div className="text-sm text-gray-600">
              <strong>Items:</strong> {tx.items.join(', ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionsPage;
