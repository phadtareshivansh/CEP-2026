/**
 * Supabase Authentication Utilities
 * Provides helper functions for JWT validation and user management
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

const supabase = supabaseUrl && supabaseKey 
    ? createClient(supabaseUrl, supabaseKey)
    : null;

/**
 * Verify JWT token and get user
 * @param {string} token - JWT token from Authorization header
 * @returns {Promise<Object>} User object if valid
 */
async function verifyToken(token) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error) throw error;
    return user;
}

/**
 * Sign up a new user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} User and session
 */
async function signUp(email, password) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase.auth.signUp({
        email,
        password
    });

    if (error) throw error;
    return data;
}

/**
 * Sign in user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} User and session
 */
async function signIn(email, password) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
    });

    if (error) throw error;
    return data;
}

/**
 * Sign out user
 * @param {string} token - JWT token
 * @returns {Promise<void>}
 */
async function signOut(token) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { error } = await supabase.auth.signOut();
    if (error) throw error;
}

/**
 * Update user profile
 * @param {string} token - JWT token
 * @param {Object} updates - Profile updates
 * @returns {Promise<Object>} Updated user
 */
async function updateProfile(token, updates) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase.auth.updateUser(updates);
    if (error) throw error;
    return data;
}

/**
 * Get user profile from database
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile
 */
async function getUserProfile(userId) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', userId)
        .single();

    if (error && error.code !== 'PGRST116') throw error;
    return data;
}

/**
 * Update user profile in database
 * @param {string} userId - User ID
 * @param {Object} profile - Profile data
 * @returns {Promise<Object>} Updated profile
 */
async function upsertUserProfile(userId, profile) {
    if (!supabase) {
        throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
        .from('user_profiles')
        .upsert(
            { user_id: userId, ...profile },
            { onConflict: 'user_id' }
        )
        .select()
        .single();

    if (error) throw error;
    return data;
}

module.exports = {
    supabase,
    verifyToken,
    signUp,
    signIn,
    signOut,
    updateProfile,
    getUserProfile,
    upsertUserProfile
};
