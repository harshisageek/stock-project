
import { createClient } from '@supabase/supabase-js';

// Access environment variables in Vite
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.warn("Missing VITE_SUPABASE_URL or VITE_SUPABASE_KEY. Authentication will fail.");
}

export const supabase = createClient(supabaseUrl || '', supabaseKey || '');

// --- Watchlist Helpers ---

export const addToWatchlist = async (userId, ticker) => {
    const { data, error } = await supabase
        .from('watchlists')
        .insert([{ user_id: userId, ticker: ticker.toUpperCase() }])
        .select();
    return { data, error };
};

export const removeFromWatchlist = async (userId, ticker) => {
    const { data, error } = await supabase
        .from('watchlists')
        .delete()
        .eq('user_id', userId)
        .eq('ticker', ticker.toUpperCase());
    return { data, error };
};

export const getWatchlist = async (userId) => {
    const { data, error } = await supabase
        .from('watchlists')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });
    return { data, error };
};
