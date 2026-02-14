# arXiv Paper Analyzer with Google Gemini

A Python tool for searching arXiv papers and analyzing them using Google's Gemini AI.

## Features

- 🔍 **Search arXiv papers** by topic, author, or category
- 📄 **Extract paper metadata** (title, authors, abstract, dates, categories)
- 🤖 **AI-powered analysis** using Google Gemini to summarize and analyze papers
- 📊 **Batch processing** to analyze multiple papers at once
- 🔄 **Compare papers** to find common themes and differences
- 💡 **Extract key concepts** from multiple papers
- ❓ **Generate research questions** based on paper analysis
- 💾 **Download PDFs** directly from arXiv
- 📁 **Save results** to JSON for later use

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements_gemini.txt
```

3. Set up your Google API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Copy `.env_gemini.example` to `.env`
   - Add your Google API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Quick Start

Run the example script:
```bash
python arxiv_analyzer_gemini.py
```

This will search for papers on "large language models", analyze them, and save results.

## Usage Examples

### Basic Search

```python
from arxiv_analyzer_gemini import ArxivAnalyzerGemini

# Initialize
analyzer = ArxivAnalyzerGemini()

# Search for papers
papers = analyzer.search_papers(
    query="neural networks",
    max_results=5
)

# Print results
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Published: {paper['published']}\n")
```

### Advanced Search Queries

```python
# Search by category
papers = analyzer.search_papers(
    query="cat:cs.AI",  # Computer Science - AI
    max_results=10
)

# Search by author
papers = analyzer.search_papers(
    query="au:LeCun",
    max_results=5
)

# Combined search
papers = analyzer.search_papers(
    query="cat:cs.LG AND transformers",
    max_results=5
)

# Sort by date
import arxiv
papers = analyzer.search_papers(
    query="diffusion models",
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate
)
```

### Analyze a Single Paper

```python
# Get papers
papers = analyzer.search_papers("quantum computing", max_results=1)

# Different types of analysis
summary = analyzer.analyze_paper(papers[0], analysis_type="summary")
findings = analyzer.analyze_paper(papers[0], analysis_type="key_findings")
methodology = analyzer.analyze_paper(papers[0], analysis_type="methodology")
critique = analyzer.analyze_paper(papers[0], analysis_type="critique")

print(summary)
```

### Custom Analysis Prompt

```python
custom_analysis = analyzer.analyze_paper(
    papers[0],
    custom_prompt="Explain this paper's contribution in simple terms for a high school student.",
    temperature=0.5  # Lower temperature for more focused responses
)
```

### Control Generation Parameters

```python
# More creative analysis
creative_analysis = analyzer.analyze_paper(
    papers[0],
    analysis_type="summary",
    temperature=1.2  # Higher temperature for more creative responses
)

# More focused analysis
focused_analysis = analyzer.analyze_paper(
    papers[0],
    analysis_type="methodology",
    temperature=0.3  # Lower temperature for more deterministic responses
)
```

### Batch Analysis

```python
# Search and analyze multiple papers
papers = analyzer.search_papers("machine learning", max_results=5)

# Analyze all papers
analyzed_papers = analyzer.batch_analyze_papers(
    papers, 
    analysis_type="key_findings",
    temperature=0.7
)

# Access results
for paper in analyzed_papers:
    print(f"\nPaper: {paper['title']}")
    print(f"Analysis: {paper['analysis']}")
```

### Compare Papers

```python
# Get papers on a topic
papers = analyzer.search_papers("reinforcement learning", max_results=3)

# Compare them
comparison = analyzer.compare_papers(papers, temperature=0.8)
print(comparison)
```

### Extract Key Concepts (Gemini Exclusive)

```python
# Get papers on a topic
papers = analyzer.search_papers("computer vision", max_results=10)

# Extract key concepts
concepts = analyzer.extract_key_concepts(papers, max_concepts=15)
print(concepts)
```

### Generate Research Questions (Gemini Exclusive)

```python
# Get recent papers
import arxiv
papers = analyzer.search_papers(
    query="cat:cs.AI",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

# Generate research questions
questions = analyzer.generate_research_questions(papers, num_questions=10)
print(questions)
```

### Download Papers

```python
# Download a paper PDF
papers = analyzer.search_papers("attention is all you need", max_results=1)
pdf_path = analyzer.download_paper(
    papers[0]['arxiv_id'],
    download_dir="./my_papers"
)
print(f"Downloaded to: {pdf_path}")
```

### Save Results

```python
# Save analyzed papers to JSON
analyzed_papers = analyzer.batch_analyze_papers(papers)
analyzer.save_results(analyzed_papers, "my_analysis.json")

# Load results later
import json
with open("my_analysis.json", 'r') as f:
    loaded_papers = json.load(f)
```

## Complete Research Workflow

```python
from arxiv_analyzer_gemini import ArxivAnalyzerGemini
import arxiv

# Initialize
analyzer = ArxivAnalyzerGemini()

# 1. Search for recent papers on a topic
papers = analyzer.search_papers(
    query="cat:cs.AI AND large language models",
    max_results=15,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

print(f"Found {len(papers)} papers")

# 2. Filter papers by date
recent_papers = [p for p in papers if p['published'] >= '2024-01-01']

# 3. Extract key concepts across all papers
print("\n=== KEY CONCEPTS ===")
concepts = analyzer.extract_key_concepts(recent_papers, max_concepts=10)
print(concepts)

# 4. Analyze individual papers
print("\n=== ANALYZING PAPERS ===")
analyzed = analyzer.batch_analyze_papers(
    recent_papers[:5],  # Analyze top 5
    analysis_type="key_findings",
    temperature=0.7
)

# 5. Compare related papers
if len(recent_papers) >= 3:
    print("\n=== COMPARATIVE ANALYSIS ===")
    comparison = analyzer.compare_papers(recent_papers[:3], temperature=0.8)
    print(comparison)

# 6. Generate research questions
print("\n=== RESEARCH QUESTIONS ===")
questions = analyzer.generate_research_questions(recent_papers[:5], num_questions=7)
print(questions)

# 7. Save everything
analyzer.save_results(analyzed, "llm_papers_analysis.json")

# 8. Download interesting papers
print("\n=== DOWNLOADING PAPERS ===")
for paper in analyzed[:2]:  # Download top 2
    pdf_path = analyzer.download_paper(
        paper['arxiv_id'],
        download_dir="./downloaded_papers"
    )
    print(f"Downloaded: {pdf_path}")
```

## Literature Review Workflow

```python
# Perfect for conducting literature reviews
analyzer = ArxivAnalyzerGemini()

# Define your research area
research_topic = "explainable AI"

# 1. Broad search
papers = analyzer.search_papers(
    query=f"{research_topic}",
    max_results=20,
    sort_by=arxiv.SortCriterion.Relevance
)

# 2. Get overview of the field
concepts = analyzer.extract_key_concepts(papers, max_concepts=15)
print("Main concepts in the field:")
print(concepts)

# 3. Detailed analysis of top papers
top_papers = papers[:10]
analyzed = analyzer.batch_analyze_papers(
    top_papers,
    analysis_type="summary",
    temperature=0.5
)

# 4. Find research gaps
questions = analyzer.generate_research_questions(top_papers, num_questions=10)
print("\nPotential research directions:")
print(questions)

# 5. Compare methodologies
comparison = analyzer.compare_papers(top_papers[:5])
print("\nMethodological comparison:")
print(comparison)

# 6. Save literature review
analyzer.save_results(analyzed, f"{research_topic.replace(' ', '_')}_review.json")
```

## arXiv Query Syntax

The arXiv API supports various search operators:

- `AND`, `OR`, `ANDNOT` - Boolean operators
- `au:author_name` - Search by author
- `ti:title_words` - Search in title
- `abs:abstract_words` - Search in abstract
- `cat:category` - Search by category
- `all:keywords` - Search all fields

### Common Categories

- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision
- `cs.RO` - Robotics
- `stat.ML` - Machine Learning (Statistics)
- `math.OC` - Optimization and Control
- `q-bio` - Quantitative Biology
- `physics` - Physics

### Example Queries

```python
# Papers about diffusion models in computer vision
papers = analyzer.search_papers("cat:cs.CV AND diffusion models")

# Papers by specific author on topic
papers = analyzer.search_papers("au:Goodfellow AND generative")

# Recent papers in AI
papers = analyzer.search_papers(
    "cat:cs.AI", 
    sort_by=arxiv.SortCriterion.SubmittedDate
)
```

## API Reference

### `ArxivAnalyzerGemini` Class

#### `__init__(api_key=None)`
Initialize the analyzer with optional Google API key.

#### `search_papers(query, max_results=5, sort_by=arxiv.SortCriterion.Relevance)`
Search arXiv for papers.

**Returns:** List of paper dictionaries with fields:
- `title`: Paper title
- `authors`: List of author names
- `summary`: Abstract
- `published`: Publication date
- `updated`: Last update date
- `arxiv_id`: arXiv identifier
- `pdf_url`: Direct PDF link
- `categories`: List of arXiv categories
- `primary_category`: Main category

#### `analyze_paper(paper, analysis_type="summary", custom_prompt=None, temperature=0.7)`
Analyze a single paper with Gemini.

**Analysis types:**
- `"summary"` - General summary
- `"key_findings"` - Main findings
- `"methodology"` - Methods analysis
- `"critique"` - Critical analysis

**Parameters:**
- `temperature` - Controls randomness (0.0-2.0). Lower = more focused, Higher = more creative

#### `batch_analyze_papers(papers, analysis_type="summary", temperature=0.7)`
Analyze multiple papers and add "analysis" field to each.

#### `compare_papers(papers, temperature=0.7)`
Compare 2+ papers to find themes and differences.

#### `extract_key_concepts(papers, max_concepts=10)`
Extract important concepts from multiple papers using Gemini.

#### `generate_research_questions(papers, num_questions=5)`
Generate potential research questions based on papers.

#### `download_paper(arxiv_id, download_dir="./papers")`
Download paper PDF. Returns file path.

#### `save_results(data, filename="arxiv_results.json")`
Save analysis results to JSON file.

## Temperature Guide

Gemini's temperature parameter controls response randomness:

- **0.0 - 0.3**: Very focused, deterministic responses. Best for factual analysis.
- **0.4 - 0.7**: Balanced responses. Good default for most tasks.
- **0.8 - 1.2**: More creative, varied responses. Good for brainstorming.
- **1.3 - 2.0**: Highly creative, potentially less coherent. Use with caution.

```python
# For factual summaries
analyzer.analyze_paper(paper, analysis_type="summary", temperature=0.3)

# For creative research questions
analyzer.generate_research_questions(papers, temperature=1.2)
```

## Gemini-Specific Features

### 1. Key Concept Extraction
Automatically identify and rank important concepts across multiple papers:
```python
concepts = analyzer.extract_key_concepts(papers, max_concepts=20)
```

### 2. Research Question Generation
Generate novel research questions based on current literature:
```python
questions = analyzer.generate_research_questions(papers, num_questions=10)
```

### 3. Temperature Control
Fine-tune response creativity for different tasks:
```python
# Focused analysis
analyzer.analyze_paper(paper, temperature=0.2)

# Creative synthesis
analyzer.compare_papers(papers, temperature=1.0)
```

## Tips

1. **API Quotas**: Gemini has free tier quotas. Monitor usage at [Google AI Studio](https://makersuite.google.com/).

2. **Temperature tuning**: Start with 0.7 and adjust based on your needs.

3. **Batch processing**: For large batches, the script includes error handling to continue on failures.

4. **Rate limiting**: If you hit rate limits, add delays between requests or reduce batch size.

5. **Custom prompts**: Leverage Gemini's strong instruction-following for specialized analyses.

## Troubleshooting

**"GOOGLE_API_KEY must be set"**
- Make sure you've created a `.env` file with your API key
- Get your key from: https://makersuite.google.com/app/apikey
- Or pass the key directly: `ArxivAnalyzerGemini(api_key="your-key")`

**No papers found**
- Check your query syntax
- Try broader search terms
- Verify the category exists

**API errors**
- Check your API key is valid
- Verify you haven't exceeded free tier quotas
- Check network connection

**Rate limit errors**
- Wait a few minutes and retry
- Reduce max_results or batch size
- Consider upgrading your API plan

## Comparison: Gemini vs Claude

| Feature | Gemini Version | Claude Version |
|---------|---------------|----------------|
| API Cost | Free tier available | Pay per token |
| Key Concept Extraction | ✅ Built-in | ❌ Not included |
| Research Questions | ✅ Built-in | ❌ Not included |
| Temperature Control | ✅ 0.0-2.0 range | ✅ Different scale |
| Analysis Types | 4 types | 4 types |
| Batch Processing | ✅ With error handling | ✅ Included |
| PDF Download | ✅ Included | ✅ Included |

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Feel free to submit issues or pull requests.

## Getting Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

The free tier includes:
- 60 requests per minute
- 1,500 requests per day
- 1 million tokens per day
