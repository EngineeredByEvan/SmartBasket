import axios from 'axios';
import { Transaction } from '../types';

export const getTransactions = async (): Promise<Transaction[]> => {
  const token = localStorage.getItem('token');
  const response = await axios.get('/api/v1/transactions', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};
