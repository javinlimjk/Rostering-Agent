"""
Labour law compliance checker using LangChain and Chroma for RAG.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

try:
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.text_splitter import CharacterTextSplitter
    from langchain.llms import OpenAI
    from langchain.chains import RetrievalQA
    from langchain.document_loaders import TextLoader, DirectoryLoader
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback for newer LangChain versions
    try:
        from langchain_community.embeddings import OpenAIEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain.text_splitter import CharacterTextSplitter
        from langchain_community.llms import OpenAI
        from langchain.chains import RetrievalQA
        from langchain_community.document_loaders import TextLoader, DirectoryLoader
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        # RAG features not available - will use basic rule-based checking only
        LANGCHAIN_AVAILABLE = False
        OpenAIEmbeddings = None
        Chroma = None
        CharacterTextSplitter = None
        OpenAI = None
        RetrievalQA = None
        TextLoader = None
        DirectoryLoader = None


class ComplianceChecker:
    """Check labour law compliance using RAG."""
    
    def __init__(
        self, 
        labour_laws_dir: str = "data/labour_laws",
        persist_directory: str = "./chroma_db"
    ):
        """Initialize the compliance checker with labour law documents."""
        self.labour_laws_dir = Path(labour_laws_dir)
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.qa_chain = None
        
        # Check if OpenAI API key is available
        self.use_openai = os.getenv('OPENAI_API_KEY') is not None
        
        if not self.labour_laws_dir.exists():
            raise ValueError(f"Labour laws directory not found: {labour_laws_dir}")
        
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Load and index labour law documents."""
        if not LANGCHAIN_AVAILABLE:
            print("Warning: LangChain not installed. Compliance checking will use basic rule-based validation only.")
            return
            
        if not self.use_openai:
            print("Warning: OPENAI_API_KEY not set. Compliance checking will use basic matching.")
            return
        
        try:
            # Load documents
            loader = DirectoryLoader(
                str(self.labour_laws_dir),
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            # Split documents
            text_splitter = CharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)
            
            # Create embeddings and vectorstore
            embeddings = OpenAIEmbeddings()
            
            # Check if persisted database exists
            if Path(self.persist_directory).exists():
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=embeddings
                )
            else:
                self.vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=embeddings,
                    persist_directory=self.persist_directory
                )
                self.vectorstore.persist()
            
            # Create QA chain
            llm = OpenAI(temperature=0)
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            print("Falling back to basic compliance checking")
            self.vectorstore = None
            self.qa_chain = None
    
    def check_compliance(
        self,
        schedule: List[Dict[str, Any]],
        workers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check schedule compliance with labour laws.
        
        Args:
            schedule: List of daily schedules
            workers: List of worker dictionaries
            
        Returns:
            Dictionary with compliance status and violations
        """
        compliance_results = {
            'overall_compliant': True,
            'countries_checked': set(),
            'violations': [],
            'recommendations': []
        }
        
        # Basic compliance checks (rule-based)
        worker_map = {w['id']: w for w in workers}
        worker_shifts = {w['id']: [] for w in workers}
        
        # Collect shift assignments
        for day_idx, day in enumerate(schedule):
            for shift_type, assignments in day['shifts'].items():
                for assignment in assignments:
                    worker_id = assignment['worker_id']
                    worker_shifts[worker_id].append({
                        'day': day_idx,
                        'shift_type': shift_type
                    })
        
        # Check each worker
        for worker_id, shifts in worker_shifts.items():
            worker = worker_map[worker_id]
            country = worker.get('country', 'US')
            compliance_results['countries_checked'].add(country)
            
            # Check using RAG if available
            if self.qa_chain:
                rag_violations = self._check_with_rag(worker, shifts, country)
                compliance_results['violations'].extend(rag_violations)
            
            # Always run basic checks
            basic_violations = self._basic_compliance_check(worker, shifts)
            compliance_results['violations'].extend(basic_violations)
        
        compliance_results['overall_compliant'] = len(compliance_results['violations']) == 0
        compliance_results['countries_checked'] = list(compliance_results['countries_checked'])
        
        return compliance_results
    
    def _check_with_rag(
        self,
        worker: Dict[str, Any],
        shifts: List[Dict[str, Any]],
        country: str
    ) -> List[Dict[str, Any]]:
        """Use RAG to check compliance."""
        violations = []
        
        try:
            # Construct query
            num_shifts = len(shifts)
            working_days = len(set(s['day'] for s in shifts))
            
            query = f"""
            For a worker in {country}, analyze the following schedule:
            - Total shifts: {num_shifts}
            - Working days: {working_days}
            
            Are there any labour law violations? Consider:
            1. Maximum working hours per week
            2. Consecutive working days
            3. Rest periods between shifts
            4. Night work restrictions
            
            Answer with specific violations if any, or "No violations" if compliant.
            """
            
            result = self.qa_chain({"query": query})
            answer = result['result'].lower()
            
            # Parse the answer for violations
            if 'violation' in answer and 'no violation' not in answer:
                violations.append({
                    'worker_id': worker['id'],
                    'worker_name': worker['name'],
                    'country': country,
                    'type': 'rag_detected_violation',
                    'description': result['result']
                })
        
        except Exception as e:
            print(f"Error in RAG compliance check: {e}")
        
        return violations
    
    def _basic_compliance_check(
        self,
        worker: Dict[str, Any],
        shifts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform basic rule-based compliance checks."""
        violations = []
        
        # Check consecutive working days
        if shifts:
            working_days = sorted(set(s['day'] for s in shifts))
            consecutive_count = 1
            max_consecutive = 6  # Conservative default
            
            for i in range(1, len(working_days)):
                if working_days[i] == working_days[i-1] + 1:
                    consecutive_count += 1
                    if consecutive_count > max_consecutive:
                        violations.append({
                            'worker_id': worker['id'],
                            'worker_name': worker['name'],
                            'country': worker.get('country', 'Unknown'),
                            'type': 'consecutive_days_exceeded',
                            'description': f'Working {consecutive_count} consecutive days exceeds limit of {max_consecutive}'
                        })
                        break
                else:
                    consecutive_count = 1
        
        return violations
    
    def get_labour_law_info(self, country: str, query: str) -> str:
        """
        Query labour law information for a specific country.
        
        Args:
            country: Country code (e.g., 'US', 'UK')
            query: Question about labour laws
            
        Returns:
            Answer based on RAG or fallback message
        """
        if not self.qa_chain:
            return f"RAG system not available. Please check labour laws for {country} manually."
        
        try:
            full_query = f"For {country}: {query}"
            result = self.qa_chain({"query": full_query})
            return result['result']
        except Exception:
            return f"Error querying labour laws. Please check the labour law documents for {country}."
