/**
 * SQL Detective Game - API Client
 * Handles all communication with the Flask backend
 */

const API_BASE = '/api';

class GameAPI {
    /**
     * Execute a SQL query
     */
    async executeQuery(query) {
        try {
            const response = await fetch(`${API_BASE}/query/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Execute query error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    }

    /**
     * Check if query is correct answer for level
     */
    async checkAnswer(query, levelId) {
        try {
            const response = await fetch(`${API_BASE}/query/check`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, level_id: levelId }),
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Check answer error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    }

    /**
     * Validate query syntax without executing
     */
    async validateQuery(query) {
        try {
            const response = await fetch(`${API_BASE}/query/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Validate query error:', error);
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Get all levels
     */
    async getLevels() {
        try {
            const response = await fetch(`${API_BASE}/game/levels`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get levels error:', error);
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Get specific level details
     */
    async getLevel(levelId) {
        try {
            const response = await fetch(`${API_BASE}/game/levels/${levelId}`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get level error:', error);
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Get player progress
     */
    async getProgress() {
        try {
            const response = await fetch(`${API_BASE}/game/progress`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get progress error:', error);
            return { success: false, current_level: 1, completed_levels: [] };
        }
    }

    /**
     * Reset player progress
     */
    async resetProgress() {
        try {
            const response = await fetch(`${API_BASE}/game/progress/reset`, {
                method: 'POST',
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Reset progress error:', error);
            return { success: false };
        }
    }

    /**
     * Get available tables for current level
     */
    async getTables() {
        try {
            const response = await fetch(`${API_BASE}/game/tables`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get tables error:', error);
            return { success: false, tables: [] };
        }
    }

    /**
     * Get sample data from a table
     */
    async getTableSample(tableName) {
        try {
            const response = await fetch(`${API_BASE}/game/tables/${tableName}/sample`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get table sample error:', error);
            return { success: false };
        }
    }

    /**
     * Get table schema
     */
    async getTableSchema(tableName) {
        try {
            const response = await fetch(`${API_BASE}/game/tables/${tableName}/schema`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Get table schema error:', error);
            return { success: false };
        }
    }
}

export const api = new GameAPI();
export default api;
