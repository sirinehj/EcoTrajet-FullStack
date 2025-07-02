import axios from 'axios';

const API_BASE = '/api'; // Proxy will handle this

export const reservationService = {
  // Get user's reservations
  getMyReservations: async () => {
    try {
      const response = await axios.get(`${API_BASE}/reservations/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching reservations:', error);
      throw error;
    }
  },

  // Create a new reservation
  createReservation: async (reservationData) => {
    try {
      const response = await axios.post(`${API_BASE}/reservations/`, reservationData, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating reservation:', error);
      throw error;
    }
  },

  // Get reservation details
  getReservationDetails: async (reservationId) => {
    try {
      const response = await axios.get(`${API_BASE}/reservations/${reservationId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching reservation details:', error);
      throw error;
    }
  },

  // Update a reservation
  updateReservation: async (reservationId, reservationData) => {
    try {
      const response = await axios.patch(`${API_BASE}/reservations/${reservationId}/`, reservationData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error updating reservation:', error);
      throw error;
    }
  },

  // Cancel a reservation
  cancelReservation: async (reservationId) => {
    try {
      const response = await axios.delete(`${API_BASE}/reservations/${reservationId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error cancelling reservation:', error);
      throw error;
    }
  },

  // Get reservations for a specific trip
  getTripReservations: async (tripId) => {
    try {
      const response = await axios.get(`${API_BASE}/trips/${tripId}/reservations/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trip reservations:', error);
      throw error;
    }
  }
};