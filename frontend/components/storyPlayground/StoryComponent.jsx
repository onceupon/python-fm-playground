"use client";

import React, { useState } from "react";
import GlobalConfig from "@/app/app.config";
import { claude35Sonnet } from "@/helpers/modelData";
import Spinner from "../Spinner";

// Story genres and themes for dropdown selection
const GENRES = [
    { value: "", label: "Random" },
    { value: "action", label: "Action" },
    { value: "thriller", label: "Thriller" },
    { value: "dystopian", label: "Dystopian" },
    { value: "utopian", label: "Utopian" },
    { value: "western", label: "Western" },
    { value: "cyberpunk", label: "Cyberpunk" },
    { value: "steampunk", label: "Steampunk" },
    { value: "magical realism", label: "Magical Realism" },
    { value: "urban fantasy", label: "Urban Fantasy" },
    { value: "space opera", label: "Space Opera" }
];

const THEMES = [
    { value: "", label: "Random" },
    { value: "adventure", label: "Adventure" },
    { value: "mystery", label: "Mystery" },
    { value: "fantasy", label: "Fantasy" },
    { value: "science fiction", label: "Science Fiction" },
    { value: "romance", label: "Romance" },
    { value: "horror", label: "Horror" },
    { value: "historical", label: "Historical" },
    { value: "comedy", label: "Comedy" },
    { value: "drama", label: "Drama" },
    { value: "fairy tale", label: "Fairy Tale" }
];

const LENGTH_OPTIONS = [
    { value: "short", label: "Short (~500 words)" },
    { value: "medium", label: "Medium (~1000 words)" },
    { value: "long", label: "Long (~2000 words)" }
];

export default function StoryComponent() {
    const [isLoading, setIsLoading] = useState(false);
    const [storyTitle, setStoryTitle] = useState("");
    const [storyContent, setStoryContent] = useState("");
    const [error, setError] = useState("");
    
    // Story generation parameters
    const [theme, setTheme] = useState("");
    const [genre, setGenre] = useState("");
    const [characters, setCharacters] = useState(1);
    const [length, setLength] = useState("medium");
    const [temperature, setTemperature] = useState(claude35Sonnet.temperatureRange.default);
    const [maxTokens, setMaxTokens] = useState(claude35Sonnet.maxTokenRange.default);

    const handleTemperatureChange = (e) => {
        const value = parseFloat(e.target.value);
        if (value >= claude35Sonnet.temperatureRange.min && value <= claude35Sonnet.temperatureRange.max) {
            setTemperature(value);
        }
    };

    const handleMaxTokensChange = (e) => {
        const value = parseInt(e.target.value);
        if (value >= claude35Sonnet.maxTokenRange.min && value <= claude35Sonnet.maxTokenRange.max) {
            setMaxTokens(value);
        }
    };

    const handleCharactersChange = (e) => {
        const value = parseInt(e.target.value);
        if (value >= 1 && value <= 10) {
            setCharacters(value);
        }
    };

    const generateStory = async () => {
        setIsLoading(true);
        setError("");
        
        try {
            const endpoint = "/story-playground/generate";
            const api = `${GlobalConfig.apiHost}:${GlobalConfig.apiPort}${endpoint}`;
            
            const response = await fetch(api, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    theme,
                    genre,
                    characters,
                    length,
                    temperature,
                    maxTokens
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setStoryTitle(data.title);
            setStoryContent(data.story);
            
        } catch (error) {
            console.error("Error generating story:", error);
            setError("Failed to generate story. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const getButtonClass = () => {
        const inactiveButtonClass = "flex w-[180px] items-center justify-center bg-indigo-300 rounded-xl text-white px-3 py-2 flex-shrink-0";
        const activeButtonClass = "flex w-[180px] items-center justify-center bg-indigo-500 hover:bg-indigo-600 rounded-xl text-white px-3 py-2 flex-shrink-0";
        return isLoading ? inactiveButtonClass : activeButtonClass;
    };

    return (
        <div className="flex flex-col flex-auto h-full p-6">
            <h3 className="text-3xl font-medium text-gray-700">Story Playground</h3>
            <p className="text-gray-500 mt-2">Generate random stories using Claude 3.5 Sonnet</p>
            
            <div className="flex flex-col flex-shrink-0 rounded-2xl bg-gray-100 p-4 mt-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    {/* Theme Selection */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
                        <select
                            value={theme}
                            onChange={(e) => setTheme(e.target.value)}
                            disabled={isLoading}
                            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            {THEMES.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    {/* Genre Selection */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                        <select
                            value={genre}
                            onChange={(e) => setGenre(e.target.value)}
                            disabled={isLoading}
                            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            {GENRES.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    {/* Characters Count */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Number of Characters</label>
                        <input
                            type="number"
                            min="1"
                            max="10"
                            value={characters}
                            onChange={handleCharactersChange}
                            disabled={isLoading}
                            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                    
                    {/* Story Length */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Story Length</label>
                        <select
                            value={length}
                            onChange={(e) => setLength(e.target.value)}
                            disabled={isLoading}
                            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            {LENGTH_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    {/* Temperature */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Temperature: {temperature}
                        </label>
                        <input
                            type="range"
                            min={claude35Sonnet.temperatureRange.min}
                            max={claude35Sonnet.temperatureRange.max}
                            step="0.1"
                            value={temperature}
                            onChange={(e) => setTemperature(parseFloat(e.target.value))}
                            disabled={isLoading}
                            className="w-full"
                        />
                    </div>
                    
                    {/* Max Tokens */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
                        <input
                            type="number"
                            min={claude35Sonnet.maxTokenRange.min}
                            max={claude35Sonnet.maxTokenRange.max}
                            value={maxTokens}
                            onChange={handleMaxTokensChange}
                            disabled={isLoading}
                            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                </div>
                
                {/* Generate Button */}
                <div className="flex justify-center mt-4">
                    <button
                        onClick={generateStory}
                        disabled={isLoading}
                        className={getButtonClass()}
                    >
                        {isLoading ? (
                            <>
                                <Spinner />
                                <span className="ml-2">Generating...</span>
                            </>
                        ) : (
                            <>
                                <span>Generate Story</span>
                                <span className="ml-2">
                                    <svg
                                        className="w-4 h-4"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M14 5l7 7m0 0l-7 7m7-7H3"
                                        ></path>
                                    </svg>
                                </span>
                            </>
                        )}
                    </button>
                </div>
                
                {/* Error Message */}
                {error && (
                    <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
                        {error}
                    </div>
                )}
                
                {/* Story Output */}
                {storyTitle && (
                    <div className="mt-8 p-6 bg-white rounded-lg shadow">
                        <h2 className="text-2xl font-bold mb-4">{storyTitle}</h2>
                        <div className="prose max-w-none">
                            {storyContent.split('\n').map((paragraph, index) => (
                                <p key={index} className="mb-4">
                                    {paragraph}
                                </p>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}