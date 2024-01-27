const baseurl: string = "localhost:3000"
const apiurl: string = `${baseurl}/api` 
const image = `${baseurl}/images`

export interface SearchResult {
    movie_name: string
    movie_id: string
    pic_id: string
    path: string
}

export const ingest = async (url: string) => {
    const response = await fetch(`${apiurl}/ingest?url=${url}`)
    const json = await response.json()
    return json
}

export const search = async (query: string): Promise<SearchResult[]> => {
    const response = await fetch(`${apiurl}/search?q=${query}`)
    const json = await response.json()
    return json
}

export const getImage = (pic_id: string) => {
    const url = `${apiurl}/images/${pic_id}`
    const response = fetch(url)
    return response
}