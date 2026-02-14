import arxiv
import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


class ArxivAnalyzerGemini:
    """A tool for searching arXiv papers and analyzing them with Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ArxivAnalyzerGemini.
        
        Args:
            api_key: Google API key. If not provided, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be set in environment or passed to constructor")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def search_papers(
        self, 
        query: str, 
        max_results: int = 5,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict]:
        """
        Search arXiv for papers matching the query.
        
        Args:
            query: Search query (can use arXiv syntax like "cat:cs.AI")
            max_results: Maximum number of results to return
            sort_by: How to sort results (Relevance, LastUpdatedDate, SubmittedDate)
        
        Returns:
            List of paper dictionaries with metadata
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
        for result in search.results():
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
                "arxiv_id": result.entry_id.split("/")[-1],
                "pdf_url": result.pdf_url,
                "categories": result.categories,
                "primary_category": result.primary_category
            }
            papers.append(paper)
        
        return papers
    
    def download_paper(self, arxiv_id: str, download_dir: str = "./papers") -> str:
        """
        Download a paper PDF from arXiv.
        
        Args:
            arxiv_id: arXiv paper ID (e.g., "2301.12345")
            download_dir: Directory to save the PDF
        
        Returns:
            Path to the downloaded PDF
        """
        os.makedirs(download_dir, exist_ok=True)
        
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        filepath = paper.download_pdf(dirpath=download_dir)
        return filepath
    
    def analyze_paper(
        self, 
        paper: Dict, 
        analysis_type: str = "summary",
        custom_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Analyze a paper using Gemini.
        
        Args:
            paper: Paper dictionary from search_papers()
            analysis_type: Type of analysis - "summary", "key_findings", "methodology", "critique"
            custom_prompt: Custom analysis prompt (overrides analysis_type)
            temperature: Temperature for generation (0.0 to 2.0)
        
        Returns:
            Gemini's analysis as a string
        """
        # Prepare the paper content
        paper_content = f"""
Title: {paper['title']}

Authors: {', '.join(paper['authors'])}

Published: {paper['published']}

Categories: {', '.join(paper['categories'])}

Abstract:
{paper['summary']}
"""
        
        # Define analysis prompts
        prompts = {
            "summary": "Please provide a concise summary of this paper, highlighting the main contributions and findings.",
            "key_findings": "What are the key findings and contributions of this paper? List them clearly.",
            "methodology": "Analyze the methodology used in this paper. What approaches did the authors take?",
            "critique": "Provide a balanced critique of this paper, discussing both strengths and potential limitations."
        }
        
        analysis_prompt = custom_prompt or prompts.get(analysis_type, prompts["summary"])
        
        # Create the full prompt
        full_prompt = f"{paper_content}\n\n{analysis_prompt}"
        
        # Call Gemini API with generation config
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def batch_analyze_papers(
        self, 
        papers: List[Dict], 
        analysis_type: str = "summary",
        temperature: float = 0.7
    ) -> List[Dict]:
        """
        Analyze multiple papers and return results.
        
        Args:
            papers: List of paper dictionaries
            analysis_type: Type of analysis to perform on each paper
            temperature: Temperature for generation
        
        Returns:
            List of papers with added "analysis" field
        """
        analyzed_papers = []
        
        for i, paper in enumerate(papers, 1):
            print(f"Analyzing {i}/{len(papers)}: {paper['title'][:60]}...")
            try:
                analysis = self.analyze_paper(paper, analysis_type, temperature=temperature)
                
                analyzed_paper = paper.copy()
                analyzed_paper["analysis"] = analysis
                analyzed_papers.append(analyzed_paper)
            except Exception as e:
                print(f"Error analyzing paper: {e}")
                analyzed_paper = paper.copy()
                analyzed_paper["analysis"] = f"Error: {str(e)}"
                analyzed_papers.append(analyzed_paper)
        
        return analyzed_papers
    
    def compare_papers(
        self, 
        papers: List[Dict],
        temperature: float = 0.7
    ) -> str:
        """
        Compare multiple papers and identify common themes and differences.
        
        Args:
            papers: List of paper dictionaries (2-5 papers recommended)
            temperature: Temperature for generation
        
        Returns:
            Comparative analysis from Gemini
        """
        if len(papers) < 2:
            raise ValueError("Need at least 2 papers to compare")
        
        # Prepare papers for comparison
        papers_text = ""
        for i, paper in enumerate(papers, 1):
            papers_text += f"""
Paper {i}:
Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Abstract: {paper['summary']}

---
"""
        
        prompt = f"""Here are {len(papers)} research papers. Please compare them by:

1. Identifying common themes and research directions
2. Highlighting key differences in approach or findings
3. Discussing how these papers relate to each other
4. Noting any complementary or contradictory findings

Papers:
{papers_text}

Please provide a comparative analysis:"""
        
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 3072,
        }
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def extract_key_concepts(
        self,
        papers: List[Dict],
        max_concepts: int = 10
    ) -> Dict[str, int]:
        """
        Extract and rank key concepts across multiple papers using Gemini.
        
        Args:
            papers: List of paper dictionaries
            max_concepts: Maximum number of concepts to extract
        
        Returns:
            Dictionary of concepts and their importance scores
        """
        # Combine all abstracts
        abstracts = "\n\n".join([f"Paper: {p['title']}\n{p['summary']}" for p in papers])
        
        prompt = f"""Analyze these research paper abstracts and extract the {max_concepts} most important 
technical concepts, methods, or themes. For each concept, provide a brief explanation.

Format your response as a numbered list:
1. Concept Name: Brief explanation
2. Concept Name: Brief explanation
...

Abstracts:
{abstracts}
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_research_questions(
        self,
        papers: List[Dict],
        num_questions: int = 5
    ) -> str:
        """
        Generate potential research questions based on the papers.
        
        Args:
            papers: List of paper dictionaries
            num_questions: Number of research questions to generate
        
        Returns:
            Generated research questions
        """
        papers_summary = "\n\n".join([
            f"Title: {p['title']}\nAbstract: {p['summary']}" 
            for p in papers
        ])
        
        prompt = f"""Based on these research papers, generate {num_questions} interesting and 
unexplored research questions that could advance this field. Focus on gaps, contradictions, 
or natural extensions of the current work.

Papers:
{papers_summary}

Generate {num_questions} research questions:"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def save_results(self, data: List[Dict], filename: str = "arxiv_results.json"):
        """Save analysis results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")


def main():
    """Example usage of the ArxivAnalyzerGemini."""
    
    # Initialize the analyzer
    analyzer = ArxivAnalyzerGemini()
    
    # Example 1: Search for papers on a topic
    print("=" * 80)
    print("Searching for papers on 'large language models'...")
    print("=" * 80)
    papers = analyzer.search_papers(
        query="large language models",
        max_results=3
    )
    
    print(f"\nFound {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        print(f"   Published: {paper['published']}")
        print(f"   ID: {paper['arxiv_id']}\n")
    
    # Example 2: Analyze a single paper
    if papers:
        print("=" * 80)
        print(f"Analyzing first paper...")
        print("=" * 80)
        analysis = analyzer.analyze_paper(papers[0], analysis_type="summary")
        print(f"\nAnalysis:\n{analysis}\n")
    
    # Example 3: Batch analyze multiple papers
    print("=" * 80)
    print("Performing batch analysis...")
    print("=" * 80)
    analyzed_papers = analyzer.batch_analyze_papers(papers, analysis_type="key_findings")
    
    # Example 4: Compare papers
    if len(papers) >= 2:
        print("=" * 80)
        print("Comparing papers...")
        print("=" * 80)
        comparison = analyzer.compare_papers(papers[:2])
        print(f"\nComparative Analysis:\n{comparison}\n")
    
    # Example 5: Extract key concepts
    print("=" * 80)
    print("Extracting key concepts...")
    print("=" * 80)
    concepts = analyzer.extract_key_concepts(papers)
    print(f"\nKey Concepts:\n{concepts}\n")
    
    # Example 6: Generate research questions
    print("=" * 80)
    print("Generating research questions...")
    print("=" * 80)
    questions = analyzer.generate_research_questions(papers)
    print(f"\nResearch Questions:\n{questions}\n")
    
    # Example 7: Save results
    analyzer.save_results(analyzed_papers, "arxiv_gemini_analysis.json")
    
    # Example 8: Download a paper (commented out to avoid downloads in demo)
    # pdf_path = analyzer.download_paper(papers[0]['arxiv_id'])
    # print(f"Downloaded paper to: {pdf_path}")


if __name__ == "__main__":
    main()
