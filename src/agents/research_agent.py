"""
Research Agent for AgentZero
Specialized in web research, data gathering, and information synthesis
"""

import asyncio
import aiohttp
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, urljoin
import hashlib

import sys
sys.path.append('/home/avi/projects/agentzero')
from src.core.agent import BaseAgent, Task, AgentCapability, Priority


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and information gathering
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "ResearchAgent", config)
        
        # Research-specific configuration
        self.max_depth = config.get("max_depth", 3) if config else 3
        self.max_pages = config.get("max_pages", 50) if config else 50
        self.timeout = config.get("timeout", 30) if config else 30
        
        # Research state
        self.visited_urls: Set[str] = set()
        self.research_cache: Dict[str, Any] = {}
        self.knowledge_graph: Dict[str, List[str]] = {}
        
        # Initialize research capabilities
        self._register_research_capabilities()
    
    def _register_research_capabilities(self):
        """Register research-specific capabilities"""
        self.register_capability(AgentCapability(
            name="web_search",
            description="Search the web for information",
            handler=self._perform_web_search
        ))
        
        self.register_capability(AgentCapability(
            name="extract_content",
            description="Extract and parse content from web pages",
            handler=self._perform_data_extraction
        ))
        
        self.register_capability(AgentCapability(
            name="analyze_data",
            description="Analyze and synthesize gathered data",
            handler=self._perform_general_research
        ))
        
        self.register_capability(AgentCapability(
            name="fact_check",
            description="Verify facts and cross-reference information",
            handler=self._perform_fact_verification
        ))
        
        self.register_capability(AgentCapability(
            name="summarize",
            description="Create summaries of research findings",
            handler=self._perform_general_research
        ))
    
    async def execute(self, task: Task) -> Any:
        """
        Execute research task
        
        Args:
            task: Research task to execute
            
        Returns:
            Research results
        """
        self.logger.info(f"Executing research task: {task.name}")
        
        task_type = task.parameters.get("type", "general_research")
        
        if task_type == "web_search":
            return await self._perform_web_search(task)
        elif task_type == "deep_research":
            return await self._perform_deep_research(task)
        elif task_type == "fact_verification":
            return await self._perform_fact_verification(task)
        elif task_type == "data_extraction":
            return await self._perform_data_extraction(task)
        elif task_type == "sentiment_analysis":
            return await self._perform_sentiment_analysis(task)
        else:
            return await self._perform_general_research(task)
    
    async def _perform_web_search(self, task: Task) -> Dict[str, Any]:
        """Perform web search"""
        query = task.parameters.get("query", "")
        num_results = task.parameters.get("num_results", 10)
        
        self.logger.info(f"Searching for: {query}")
        
        # Search using multiple search engines
        results = []
        
        # Simulate search (in production, use actual search APIs)
        search_urls = await self._search_engines(query, num_results)
        
        # Fetch and analyze each result
        async with aiohttp.ClientSession() as session:
            fetch_tasks = [self._fetch_and_analyze(session, url) for url in search_urls]
            results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        # Filter out errors
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        # Rank results by relevance
        ranked_results = self._rank_by_relevance(valid_results, query)
        
        return {
            "query": query,
            "results": ranked_results[:num_results],
            "total_found": len(valid_results),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_deep_research(self, task: Task) -> Dict[str, Any]:
        """Perform deep research on a topic"""
        topic = task.parameters.get("topic", "")
        depth = min(task.parameters.get("depth", self.max_depth), self.max_depth)
        
        self.logger.info(f"Deep research on: {topic}")
        
        # Initialize research state
        research_state = {
            "topic": topic,
            "findings": [],
            "sources": [],
            "entities": set(),
            "relationships": [],
            "timeline": []
        }
        
        # Start with initial search
        search_task = Task(
            name="Initial search",
            parameters={"query": topic, "num_results": 10}
        )
        initial_results = await self._perform_web_search(search_task)
        
        # Recursive deep dive
        await self._recursive_research(
            initial_results["results"],
            research_state,
            depth,
            0
        )
        
        # Build knowledge graph
        knowledge_graph = self._build_knowledge_graph(research_state)
        
        # Generate comprehensive report
        report = self._generate_research_report(research_state, knowledge_graph)
        
        return {
            "topic": topic,
            "report": report,
            "knowledge_graph": knowledge_graph,
            "sources": list(research_state["sources"]),
            "entities": list(research_state["entities"]),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_fact_verification(self, task: Task) -> Dict[str, Any]:
        """Verify facts and claims"""
        claim = task.parameters.get("claim", "")
        context = task.parameters.get("context", "")
        
        self.logger.info(f"Verifying claim: {claim}")
        
        # Search for supporting and contradicting evidence
        supporting_evidence = await self._find_evidence(claim, "supporting")
        contradicting_evidence = await self._find_evidence(claim, "contradicting")
        
        # Analyze source credibility
        credibility_scores = self._assess_source_credibility(
            supporting_evidence + contradicting_evidence
        )
        
        # Calculate verification score
        verification_score = self._calculate_verification_score(
            supporting_evidence,
            contradicting_evidence,
            credibility_scores
        )
        
        return {
            "claim": claim,
            "verification_score": verification_score,
            "verdict": self._get_verdict(verification_score),
            "supporting_evidence": supporting_evidence[:5],
            "contradicting_evidence": contradicting_evidence[:5],
            "credibility_analysis": credibility_scores,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_data_extraction(self, task: Task) -> Dict[str, Any]:
        """Extract structured data from sources"""
        sources = task.parameters.get("sources", [])
        patterns = task.parameters.get("patterns", {})
        
        extracted_data = []
        
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    data = await self._extract_structured_data(
                        session,
                        source,
                        patterns
                    )
                    extracted_data.append(data)
                except Exception as e:
                    self.logger.error(f"Failed to extract from {source}: {e}")
        
        # Merge and deduplicate data
        merged_data = self._merge_extracted_data(extracted_data)
        
        return {
            "sources_processed": len(sources),
            "data": merged_data,
            "extraction_patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_sentiment_analysis(self, task: Task) -> Dict[str, Any]:
        """Analyze sentiment from various sources"""
        topic = task.parameters.get("topic", "")
        sources = task.parameters.get("sources", [])
        
        sentiments = []
        
        # Gather content
        if not sources:
            search_task = Task(
                name="Sentiment search",
                parameters={"query": topic, "num_results": 20}
            )
            search_results = await self._perform_web_search(search_task)
            sources = [r["url"] for r in search_results.get("results", [])]
        
        # Analyze each source
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    content = await self._fetch_content(session, source)
                    sentiment = self._analyze_sentiment(content)
                    sentiments.append({
                        "source": source,
                        "sentiment": sentiment
                    })
                except Exception as e:
                    self.logger.error(f"Sentiment analysis failed for {source}: {e}")
        
        # Aggregate results
        aggregated = self._aggregate_sentiments(sentiments)
        
        return {
            "topic": topic,
            "overall_sentiment": aggregated,
            "sources_analyzed": len(sentiments),
            "detailed_sentiments": sentiments[:10],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _perform_general_research(self, task: Task) -> Dict[str, Any]:
        """Perform general research task"""
        query = task.parameters.get("query", "")
        
        # Combine multiple research methods
        search_task = Task(
            name="General search",
            parameters={"query": query}
        )
        search_results = await self._perform_web_search(search_task)
        
        # Extract key information
        key_points = self._extract_key_points(search_results["results"])
        
        # Generate summary
        summary = self._generate_summary(key_points)
        
        return {
            "query": query,
            "summary": summary,
            "key_points": key_points,
            "sources": [r["url"] for r in search_results["results"][:5]],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _search_engines(self, query: str, num_results: int) -> List[str]:
        """Simulate search engine results"""
        # In production, integrate with actual search APIs
        # For now, return mock URLs
        base_url_templates = [
            "https://example.com/article/{}",
            "https://research.org/paper/{}",
            f"https://wiki.example.com/{query.replace(' ', '_')}",
        ]
        
        urls = []
        for i in range(min(num_results, 10)):
            for template in base_url_templates[:num_results]:
                if '{}' in template:
                    urls.append(template.format(i))
                else:
                    urls.append(template)
        
        return urls[:num_results]
    
    async def _fetch_and_analyze(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Fetch and analyze a web page"""
        try:
            # Check cache
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.research_cache:
                return self.research_cache[url_hash]
            
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse content
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract metadata
                    title = soup.find('title').text if soup.find('title') else ""
                    description = ""
                    meta_desc = soup.find('meta', {'name': 'description'})
                    if meta_desc:
                        description = meta_desc.get('content', '')
                    
                    # Extract main content
                    content = self._extract_main_content(soup)
                    
                    # Extract entities
                    entities = self._extract_entities(content)
                    
                    result = {
                        "url": url,
                        "title": title,
                        "description": description,
                        "content": content[:1000],  # First 1000 chars
                        "entities": entities,
                        "word_count": len(content.split()),
                        "fetched_at": datetime.now().isoformat()
                    }
                    
                    # Cache result
                    self.research_cache[url_hash] = result
                    
                    return result
                    
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Simple entity extraction (in production, use NLP)
        entities = []
        
        # Extract capitalized words (potential proper nouns)
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and i > 0:
                entities.append(word)
                
                # Check for multi-word entities
                if i < len(words) - 1 and words[i + 1][0].isupper():
                    entities.append(f"{word} {words[i + 1]}")
        
        return list(set(entities))[:20]  # Top 20 unique entities
    
    def _rank_by_relevance(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results by relevance to query"""
        query_words = set(query.lower().split())
        
        for result in results:
            if result:
                # Calculate relevance score
                content = (result.get("title", "") + " " + 
                          result.get("description", "") + " " + 
                          result.get("content", "")).lower()
                
                word_matches = sum(1 for word in query_words if word in content)
                result["relevance_score"] = word_matches / len(query_words) if query_words else 0
        
        # Sort by relevance
        valid_results = [r for r in results if r]
        return sorted(valid_results, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    async def _recursive_research(self, sources: List[Dict], state: Dict, max_depth: int, current_depth: int):
        """Recursively research a topic"""
        if current_depth >= max_depth:
            return
        
        for source in sources:
            if source and source.get("url") not in self.visited_urls:
                self.visited_urls.add(source["url"])
                state["sources"].append(source["url"])
                
                # Extract entities and relationships
                entities = source.get("entities", [])
                state["entities"].update(entities)
                
                # Find related topics
                if current_depth < max_depth - 1:
                    for entity in entities[:3]:  # Top 3 entities
                        sub_task = Task(
                            name="Sub search",
                            parameters={"query": f"{state['topic']} {entity}", "num_results": 3}
                        )
                        sub_results = await self._perform_web_search(sub_task)
                        
                        await self._recursive_research(
                            sub_results.get("results", []),
                            state,
                            max_depth,
                            current_depth + 1
                        )
    
    def _build_knowledge_graph(self, state: Dict) -> Dict[str, Any]:
        """Build knowledge graph from research state"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Add topic as central node
        graph["nodes"].append({
            "id": state["topic"],
            "type": "topic",
            "weight": 1.0
        })
        
        # Add entities as nodes
        for entity in state["entities"]:
            graph["nodes"].append({
                "id": entity,
                "type": "entity",
                "weight": 0.5
            })
            
            # Add edge from topic to entity
            graph["edges"].append({
                "source": state["topic"],
                "target": entity,
                "type": "related_to"
            })
        
        return graph
    
    def _generate_research_report(self, state: Dict, knowledge_graph: Dict) -> str:
        """Generate comprehensive research report"""
        report = f"# Research Report: {state['topic']}\n\n"
        report += f"## Executive Summary\n"
        report += f"Analyzed {len(state['sources'])} sources and identified {len(state['entities'])} key entities.\n\n"
        
        report += f"## Key Entities\n"
        for entity in list(state["entities"])[:10]:
            report += f"- {entity}\n"
        
        report += f"\n## Knowledge Graph\n"
        report += f"- Nodes: {len(knowledge_graph['nodes'])}\n"
        report += f"- Connections: {len(knowledge_graph['edges'])}\n"
        
        report += f"\n## Sources\n"
        for source in state["sources"][:10]:
            report += f"- {source}\n"
        
        return report
    
    async def _find_evidence(self, claim: str, evidence_type: str) -> List[Dict]:
        """Find evidence for or against a claim"""
        # Modify search query based on evidence type
        if evidence_type == "supporting":
            query = f"{claim} evidence proof confirmed"
        else:
            query = f"{claim} debunked false myth incorrect"
        
        search_task = Task(
            name="Find evidence",
            parameters={"query": query, "num_results": 10}
        )
        results = await self._perform_web_search(search_task)
        
        return results.get("results", [])
    
    def _assess_source_credibility(self, sources: List[Dict]) -> Dict[str, float]:
        """Assess credibility of sources"""
        credibility = {}
        
        for source in sources:
            if source:
                url = source.get("url", "")
                domain = urlparse(url).netloc
                
                # Simple credibility scoring
                score = 0.5  # Base score
                
                # Bonus for known reliable domains
                reliable_domains = ['edu', 'gov', 'org']
                if any(d in domain for d in reliable_domains):
                    score += 0.3
                
                # Check for HTTPS
                if url.startswith('https'):
                    score += 0.1
                
                # Penalty for known unreliable patterns
                unreliable_patterns = ['blog', 'forum', 'social']
                if any(p in domain for p in unreliable_patterns):
                    score -= 0.2
                
                credibility[url] = min(max(score, 0), 1)  # Clamp between 0 and 1
        
        return credibility
    
    def _calculate_verification_score(self, supporting: List, contradicting: List, credibility: Dict) -> float:
        """Calculate fact verification score"""
        if not supporting and not contradicting:
            return 0.5  # Uncertain
        
        # Weight evidence by credibility
        support_weight = sum(credibility.get(s.get("url", ""), 0.5) for s in supporting if s)
        contradict_weight = sum(credibility.get(c.get("url", ""), 0.5) for c in contradicting if c)
        
        total_weight = support_weight + contradict_weight
        
        if total_weight == 0:
            return 0.5
        
        return support_weight / total_weight
    
    def _get_verdict(self, score: float) -> str:
        """Get verdict based on verification score"""
        if score >= 0.8:
            return "Highly Likely True"
        elif score >= 0.6:
            return "Likely True"
        elif score >= 0.4:
            return "Uncertain"
        elif score >= 0.2:
            return "Likely False"
        else:
            return "Highly Likely False"
    
    async def _fetch_content(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch content from URL"""
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    return self._extract_main_content(soup)
        except:
            return ""
        
        return ""
    
    def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze sentiment of content"""
        # Simple sentiment analysis (in production, use NLP)
        positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'happy']
        negative_words = ['bad', 'poor', 'negative', 'failure', 'sad', 'terrible']
        
        content_lower = content.lower()
        words = content_lower.split()
        
        positive_count = sum(1 for word in positive_words if word in words)
        negative_count = sum(1 for word in negative_words if word in words)
        
        total = positive_count + negative_count
        
        if total == 0:
            return {"positive": 0.5, "negative": 0.5, "neutral": 1.0}
        
        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": 1 - (abs(positive_count - negative_count) / total)
        }
    
    def _aggregate_sentiments(self, sentiments: List[Dict]) -> Dict[str, float]:
        """Aggregate sentiment scores"""
        if not sentiments:
            return {"positive": 0, "negative": 0, "neutral": 1}
        
        total_positive = sum(s["sentiment"]["positive"] for s in sentiments)
        total_negative = sum(s["sentiment"]["negative"] for s in sentiments)
        total_neutral = sum(s["sentiment"]["neutral"] for s in sentiments)
        
        count = len(sentiments)
        
        return {
            "positive": total_positive / count,
            "negative": total_negative / count,
            "neutral": total_neutral / count
        }
    
    async def _extract_structured_data(self, session: aiohttp.ClientSession, source: str, patterns: Dict) -> Dict:
        """Extract structured data based on patterns"""
        content = await self._fetch_content(session, source)
        
        extracted = {"source": source}
        
        for field, pattern in patterns.items():
            if isinstance(pattern, str):
                # Regex pattern
                matches = re.findall(pattern, content)
                extracted[field] = matches
            elif isinstance(pattern, dict):
                # Complex extraction
                if pattern.get("type") == "numeric":
                    numbers = re.findall(r'\d+\.?\d*', content)
                    extracted[field] = [float(n) for n in numbers]
        
        return extracted
    
    def _merge_extracted_data(self, data_list: List[Dict]) -> Dict:
        """Merge and deduplicate extracted data"""
        merged = {}
        
        for data in data_list:
            for key, value in data.items():
                if key not in merged:
                    merged[key] = []
                
                if isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key].append(value)
        
        # Deduplicate
        for key in merged:
            if isinstance(merged[key], list):
                merged[key] = list(set(merged[key]))
        
        return merged
    
    def _extract_key_points(self, results: List[Dict]) -> List[str]:
        """Extract key points from results"""
        key_points = []
        
        for result in results[:5]:
            if result:
                # Extract first sentence of content as key point
                content = result.get("content", "")
                if content:
                    sentences = content.split('.')
                    if sentences:
                        key_points.append(sentences[0].strip() + ".")
        
        return key_points
    
    def _generate_summary(self, key_points: List[str]) -> str:
        """Generate summary from key points"""
        if not key_points:
            return "No significant findings."
        
        summary = "Research Summary:\n"
        for i, point in enumerate(key_points, 1):
            summary += f"{i}. {point}\n"
        
        return summary