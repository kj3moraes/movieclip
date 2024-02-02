import { json } from "stream/consumers";

export const baseurl: string = "http://localhost:8000"
const apiurl: string = `${baseurl}/api` 
export const imageurl = `${baseurl}/images`


interface BackendSearchResult {
    id: string;
    version: number;
    score: number;
    payload: {
      actor: string[];
      caption: string;
      director: string[];
      genre: string[];
      image_id: string;
      image_path: string;
      movie_id: string;
      title: string;
      year: string;
    };
}

export interface SearchResult {
    movie_name: string
    movie_id: string
    pic_id: string
    url_path: string
}

interface BackendResponse {
    message: string 
    results: BackendSearchResult[]
}

export const ingest = async () => {
    const response = await fetch(`${apiurl}/ingest`)
    const json = await response.json()
    return json
}

export const search = async (query: string): Promise<SearchResult[]> => {
    // Extract parameters using regular expressions
    const genreMatch = query.match(/g="([^"]+)"/);
    const movieMatch = query.match(/m="([^"]+)"/);
    const directorMatch = query.match(/d="([^"]+)"/);
    const yearMatch = query.match(/y="([^"]+)"/);
    const actorMatch = query.match(/a="([^"]+)"/);

    // Construct the search request body
    const requestBody = {
        text: query.replace(/(g|d|y|a)="[^"]*"/g, '').trim(), 
        k: undefined, 
        movie: movieMatch ? movieMatch[1] : undefined,
        genre: genreMatch ? genreMatch[1] : undefined,
        director: directorMatch ? directorMatch[1] : undefined,
        year: yearMatch ? yearMatch[1] : undefined,
        actor: actorMatch ? actorMatch[1] : undefined,
    };

    console.log(JSON.stringify(requestBody))

    // Send a POST request to the search API
    const response = await fetch(`${apiurl}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
    });
    
    const jsonResponse: BackendResponse = await response.json();
    console.log(jsonResponse)
    if (!jsonResponse.results) {
        return [];
    }
    // Map the backend responses to a search result that we can deal with.
    const searchResults: SearchResult[] = jsonResponse.results.map(result => ({
        movie_name: result.payload.title, // Assuming movie_name is a combination of actors, adjust as needed
        movie_id: result.payload.movie_id,
        pic_id: result.payload.image_id,
        url_path: `${baseurl}${result.payload.image_path}`,
      }));
    
    return searchResults
}
