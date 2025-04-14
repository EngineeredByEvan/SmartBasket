import axios from 'axios';
import { Prediction } from '../types';
import { getAuthHeader } from './authService';

// Use the same base URL as in authService.ts
const API_URL = process.env.REACT_APP_API_URL || 'https://smartbasket-u8bn.onrender.com/api/v1';

export const predictNextItem = async (items: string[]): Promise<Prediction> => {
  try {
    const response = await axios.post(
      `${API_URL}/predictions/next-item`,
      { items },
      { headers: await getAuthHeader() }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to get prediction');
    }
    throw new Error('Network error occurred');
  }
};

export const getPredictionHistory = async (limit = 10): Promise<Prediction[]> => {
  try {
    const response = await axios.get(`${API_URL}/predictions/history`, {
      params: { limit },
      headers: await getAuthHeader()
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(
        error.response.data.detail || 'Failed to get prediction history'
      );
    }
    throw new Error('Network error occurred');
  }
};

export const providePredictionFeedback = async (
  predictionId: number,
  feedback: string
): Promise<void> => {
  try {
    await axios.post(
      `${API_URL}/predictions/${predictionId}/feedback`,
      { feedback },
      { headers: await getAuthHeader() }
    );
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(
        error.response.data.detail || 'Failed to submit feedback'
      );
    }
    throw new Error('Network error occurred');
  }
};
