# analyzer.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

import re
import math
import io
import os
import json
import urllib.request
import urllib.parse
from difflib import SequenceMatcher
from pypdf import PdfReader
from docx import Document

# Common English stopwords to clean text without loading large NLP packages
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", 
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", 
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", 
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
    "i've", "if", "in", "into", "is", "isn't", "it", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", 
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", 
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", 
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "were", "we've", "weren't", 
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", 
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", 
    "yourselves", "will", "shall", "can", "may", "has", "have", "had", "having", "its", "include", "includes", "including"
}

# Add calendar, seasonal, and academic terms to STOPWORDS to avoid them being treated as fallback skills
STOPWORDS.update({
    "summer", "winter", "fall", "autumn",
    "january", "february", "march", "april", "june", "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "semester", "semesters", "quarter", "quarters", "term", "terms", "session", "sessions", "academic",
    "year", "years", "month", "months", "week", "weeks", "day", "days",
    "daily", "weekly", "monthly", "yearly", "annual", "annually",
    "intern", "interns", "internship", "internships", "co-op", "coops", "cooperative",
    "graduate", "graduates", "graduating", "graduation", "graduated", "expected", "class", "degree", "degrees", "conferral", "conferred"
})


# Predefined skill taxonomies for categorization
TECH_SKILLS = {
    "python", "javascript", "typescript", "java", "cpp", "csharp", "ruby", "php", "swift", "kotlin", "rust", "go", "golang",
    "react", "angular", "vue", "nextjs", "node", "express", "django", "flask", "fastapi", "spring", "rails",
    "html", "css", "tailwind", "sass", "bootstrap", "jquery",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "dynamodb", "nosql", "database", "oracle",
    "git", "github", "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "ci/cd", "devops", "terraform",
    "linux", "bash", "unix", "raspberry", "arduino", "embedded", "c",
    "rest", "graphql", "api", "microservices", "serverless", "soap",
    "tensorflow", "pytorch", "keras", "numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "seaborn",
    "scrum", "agile", "jira", "confluence", "trello", "gitlabs"
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem-solving", "critical-thinking", "adaptability",
    "time-management", "creativity", "collaboration", "mentoring", "organization", "analytical", "interpersonal",
    "presentation", "negotiation", "conflict-resolution", "self-motivated", "initiative", "flexibility"
}

BUSINESS_SKILLS = {
    "marketing", "seo", "sales", "finance", "accounting", "operations", "strategy", "management", "product-management",
    "project-management", "agile", "scrum", "customer-service", "recruiting", "human-resources", "business-analysis",
    "marketing-strategy", "product-launch", "market-research", "qa", "testing"
}

def extract_text_from_pdf(pdf_bytes):
    """Extracts text from PDF bytes using pypdf. Returns empty string on error."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_text_from_docx(docx_bytes):
    try:
        doc = Document(io.BytesIO(docx_bytes))
        text = ""
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def strip_graduation_dates(text):
    """Strips graduation date patterns, class of years, and standard date formats."""
    if not text:
        return ""
    
    # Patterns to match graduation/expected graduation dates and years
    patterns = [
        # Expected graduation / Graduation Date: May 2025 / Spring 2024
        r'\b(?:expected\s+)?graduat(?:e|ing|ion|ed|es)\s*(?:date)?\s*(?:in|of|by|:|-)?\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|spring|summer|fall|winter|autumn)[a-z]*\s*)?(?:(?:19|20)?\d{2})\b',
        # Class of 2024 / 24
        r'\bclass\s+of\s+(?:19|20)?\d{2}\b',
        # Date patterns like 05/2024, 12-2025
        r'\b\d{1,2}[-/]\d{2,4}\b'
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    return cleaned

def clean_and_normalize(text):
    """Cleans text by converting to lowercase, stripping graduation dates, and replacing special language terms."""
    if not text:
        return ""
    # Strip graduation date patterns before normalizing
    text = strip_graduation_dates(text)
    
    # Normalize programming languages/terms with special chars
    text = text.lower()
    text = text.replace("c++", "cpp")
    text = text.replace("c#", "csharp")
    text = text.replace(".net", "dotnet")
    text = text.replace("node.js", "nodejs")
    return text

def has_spring_framework(text):
    """
    Returns True if the text contains the word 'spring' in a context that is NOT
    seasonal or academic (e.g., not 'Spring 2024', 'Spring semester', 'Spring internship').
    """
    if not text:
        return False
    # Find all occurrences of word 'spring'
    matches = list(re.finditer(r'\bspring\b', text, re.IGNORECASE))
    if not matches:
        return False
        
    seasonal_patterns = [
        # Season + Year: spring 2024, spring '24, spring 24, spring of 2024, spring of 24
        r'\bspring\s*(?:of\s*)?(?:19|20)?\d{2}\b',
        # Season + academic term: spring semester, spring term, spring quarter, spring break, spring cohort, spring intake
        r'\bspring\s*(?:semester|term|quarter|session|break|vacation|cohort|intake|admission|placement|co-op|coop)\b',
        # Academic term + Season: semester spring, term spring, quarter spring, class of spring
        r'\b(?:semester|term|quarter|session|break|vacation|cohort|intake|admission|placement|class|co-op|coop)\s+(?:of\s+)?spring\b',
        # Academic/Season ranges: fall/spring, spring/summer, spring-summer, etc.
        r'\b(?:semester|term|quarter|session|break|vacation|cohort|intake|admission|placement|class|co-op|coop)\s+[-/]\s*spring\b',
        r'\bspring\s*[-/]\s*(?:summer|fall|winter|autumn)\b',
        r'\b(?:summer|fall|winter|autumn)\s*[-/]\s*spring\b',
        # Graduation context: graduation in spring, graduate in spring, graduating in spring
        r'\bgraduat(?:e|ing|ion|es)\s+(?:in\s+)?(?:the\s+)?spring\b',
        r'\bspring\s+graduat(?:e|ing|ion|es)\b',
        # Internship/Hiring cycle context: spring intern, spring internship, spring co-op
        r'\bspring\s+(?:intern|internship|co-op|coop|placement|recruit|recruiting|hiring|cycle|opportunity|opportunities)\b',
        r'\b(?:intern|internship|co-op|coop|placement|recruit|recruiting|hiring|cycle|opportunity|opportunities)\s+(?:for\s+)?(?:the\s+)?spring\b',
        # Start/Begin context: start in spring, begin in spring, starting spring 2024
        r'\b(?:begin|begins|beginning|start|starts|starting)\s+(?:in\s+)?(?:the\s+)?spring\b',
        r'\b(?:begin|begins|beginning|start|starts|starting)\s+spring\s+(?:19|20)?\d{2}\b'
    ]
    
    # Check if at least one occurrence is NOT seasonal/academic.
    for m in matches:
        start, end = m.start(), m.end()
        # Extract a window around this match (60 chars before and after)
        window_start = max(0, start - 60)
        window_end = min(len(text), end + 60)
        window = text[window_start:window_end].lower()
        
        # Center of the window relative to window_start
        center_idx = start - window_start
        
        is_seasonal = False
        for pattern in seasonal_patterns:
            for pm in re.finditer(pattern, window):
                # If the pattern match covers our target 'spring' (index center_idx to center_idx + 6)
                if pm.start() <= center_idx and pm.end() >= (center_idx + 6):
                    is_seasonal = True
                    break
            if is_seasonal:
                break
                
        if not is_seasonal:
            # We found an occurrence of 'spring' that is NOT seasonal/academic
            return True
            
    return False

def tokenize(text):
    """Splits text into lowercase alphabetic/numeric tokens, filtering out stopwords."""
    cleaned = clean_and_normalize(text)
    if not cleaned:
        return []
    # Match words: letters, numbers, and dashes inside words
    words = re.findall(r'\b[a-z0-9]+(?:\-[a-z0-9]+)*\b', cleaned)
    # Filter out numeric-only tokens, stopwords, and short words
    tokens = [w for w in words if w not in STOPWORDS and len(w) > 1 and not w.isdigit()]
    
    # Filter out seasonal/academic 'spring'
    if "spring" in tokens and not has_spring_framework(text):
        tokens = [t for t in tokens if t != "spring"]
        
    return tokens

def get_ngrams(tokens, n=2):
    """Generates n-grams from a list of tokens."""
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngrams.append(" ".join(tokens[i:i+n]))
    return ngrams

def is_fuzzy_match(keyword, text, threshold=0.85):
    """
    Checks if a keyword has a fuzzy match in the text.
    First uses a fast-path substring check. If not found, falls back
    to comparing candidate words/phrases using SequenceMatcher.
    """
    if not keyword or not text:
        return False
        
    # Fast path: exact string inclusion
    if keyword in text:
        return True
        
    # Tokenize the text and strip punctuation to run local sequence matching
    raw_words = text.split()
    words = [re.sub(r'[^\w\s-]', '', w) for w in raw_words]
    words = [w for w in words if w]
    
    kw_words = keyword.split()
    n = len(kw_words)
    
    if n == 0 or len(words) < n:
        return False
        
    # Slide a window of size 'n' across the text
    for i in range(len(words) - n + 1):
        phrase = " ".join(words[i:i+n])
        # Calculate ratio
        ratio = SequenceMatcher(None, phrase, keyword).ratio()
        if ratio >= threshold:
            return True
            
    return False

def get_matching_keywords(resume_text, job_desc_text):
    """
    Identifies skills mentioned in the job description and checks if they are in the resume.
    Returns categorized lists of matched and missing keywords.
    """
    resume_cleaned = clean_and_normalize(resume_text)
    job_cleaned = clean_and_normalize(job_desc_text)
    
    job_tokens = tokenize(job_desc_text)
    job_bigrams = get_ngrams(job_tokens, 2)
    
    # Identify skills from our dictionary present in the Job Description
    found_keywords = set()
    
    # Check single-word skills
    for token in set(job_tokens):
        if token in TECH_SKILLS or token in SOFT_SKILLS or token in BUSINESS_SKILLS:
            found_keywords.add(token)
            
    # Check bi-gram skills (e.g. "product management", "soft skills")
    all_dict_skills = TECH_SKILLS.union(SOFT_SKILLS).union(BUSINESS_SKILLS)
    for bigram in set(job_bigrams):
        # We also add common multi-word skills manually if not in list
        if bigram in all_dict_skills or bigram in ["machine learning", "data science", "web development", "software engineering", "project management", "product management", "cloud computing"]:
            found_keywords.add(bigram)
            
    # If no standard skills found, fallback to high frequency words in job description
    if len(found_keywords) < 5:
        # Find top 15 words in job description that are not stopwords
        word_counts = {}
        for token in job_tokens:
            if len(token) > 3: # Avoid very short words
                word_counts[token] = word_counts.get(token, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        for w, _ in sorted_words[:12]:
            found_keywords.add(w)

    matched = []
    missing = []
    
    for kw in found_keywords:
        if kw == "spring":
            isPresent = has_spring_framework(resume_text)
        else:
            isPresent = is_fuzzy_match(kw, resume_cleaned, threshold=0.80)
            
        category = "Other"
        if kw in TECH_SKILLS or kw in ["machine learning", "data science", "web development", "software engineering"]:
            category = "Technical"
        elif kw in SOFT_SKILLS:
            category = "Soft Skills"
        elif kw in BUSINESS_SKILLS or kw in ["project management", "product management"]:
            category = "Business / Management"
            
        item = {"keyword": kw, "category": category}
        if isPresent:
            matched.append(item)
        else:
            missing.append(item)
            
    # Sort matched and missing by category, then alphabetical keyword
    sort_key = lambda x: (x["category"], x["keyword"])
    matched.sort(key=sort_key)
    missing.sort(key=sort_key)
    
    return matched, missing

def calculate_cosine_similarity(doc1_tokens, doc2_tokens):
    """Computes TF-IDF cosine similarity between two lists of tokens."""
    vocab = set(doc1_tokens).union(set(doc2_tokens))
    if not vocab:
        return 0.0
    
    # Document frequency (DF) across our 2 documents
    df = {}
    for word in vocab:
        count = 0
        if word in doc1_tokens:
            count += 1
        if word in doc2_tokens:
            count += 1
        df[word] = count
    
    # Smooth IDF
    N = 2
    idf = {}
    for word in vocab:
        idf[word] = math.log((1 + N) / (1 + df[word])) + 1
    
    # Term Frequency (TF)
    tf1 = {}
    for token in doc1_tokens:
        tf1[token] = tf1.get(token, 0) + 1
    
    tf2 = {}
    for token in doc2_tokens:
        tf2[token] = tf2.get(token, 0) + 1
        
    # Calculate TF-IDF vectors
    v1 = []
    v2 = []
    for word in vocab:
        tfidf1 = (tf1.get(word, 0) / len(doc1_tokens) if doc1_tokens else 0) * idf[word]
        tfidf2 = (tf2.get(word, 0) / len(doc2_tokens) if doc2_tokens else 0) * idf[word]
        v1.append(tfidf1)
        v2.append(tfidf2)
    
    # Cosine Similarity
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)

def analyze_resume_structure(resume_text):
    """Analyzes resume layout, sections, formatting, and word density."""
    resume_lower = resume_text.lower()
    
    # Check word count
    words = resume_text.split()
    word_count = len(words)
    
    # Look for standard headers
    headers = {
        "experience": ["experience", "employment", "work history", "professional background"],
        "education": ["education", "academic background", "study"],
        "skills": ["skills", "technical skills", "core competencies", "technologies"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"]
    }
    
    found_headers = []
    missing_headers = []
    for section, synonyms in headers.items():
        found = False
        for syn in synonyms:
            # Look for headers on separate lines or with basic boundaries
            if re.search(r'\b' + re.escape(syn) + r'\b', resume_lower):
                found = True
                break
        if found:
            found_headers.append(section)
        else:
            missing_headers.append(section)
            
    # Check for quantified impact (numbers or percentages)
    # Find patterns like 20%, $10,000, 5+, etc.
    numbers = re.findall(r'\b\d+(?:\.\d+)?%|\b\d+\+|\$\b\d+(?:,\d+)*', resume_text)
    num_metrics = len(numbers)
    
    # Check for strong resume action verbs
    action_verbs = ["led", "developed", "designed", "implemented", "managed", "created", "optimized", "increased", "reduced", "accomplished", "authored", "accelerated", "built", "spearheaded", "executed", "improved", "launched", "formulated"]
    found_verbs = []
    for verb in action_verbs:
        if re.search(r'\b' + re.escape(verb) + r'\b', resume_lower):
            found_verbs.append(verb)
            
    return {
        "word_count": word_count,
        "found_headers": found_headers,
        "missing_headers": missing_headers,
        "metrics_count": num_metrics,
        "action_verbs_found": found_verbs[:8] # return top 8 found
    }

def analyze_cover_letter(cover_letter_text, job_desc_text):
    """Analyzes cover letter length, layout, and keyword optimization."""
    if not cover_letter_text or not cover_letter_text.strip():
        return None
        
    cl_lower = cover_letter_text.lower()
    job_lower = job_desc_text.lower()
    
    word_count = len(cover_letter_text.split())
    
    # Heuristics:
    # 1. Look for recruiter greeting
    has_greeting = any(sal in cl_lower for sal in ["dear", "hiring manager", "recruiter", "to whom it may concern", "attention"])
    
    # 2. Check sign-off
    has_signoff = any(so in cl_lower for so in ["sincerely", "best regards", "kind regards", "respectfully", "thank you"])
    
    # 3. Check for job description keyword alignment
    job_tokens = set(tokenize(job_desc_text))
    cl_tokens = set(tokenize(cover_letter_text))
    overlap = len(job_tokens.intersection(cl_tokens))
    
    # 4. Length scoring
    if 150 <= word_count <= 450:
        length_status = "Good"
    elif word_count < 150:
        length_status = "Too Short"
    else:
        length_status = "Too Long"
        
    # Cover letter rating out of 100
    cl_score = 40 # Base score for submitting
    if has_greeting: cl_score += 15
    if has_signoff: cl_score += 15
    if length_status == "Good": cl_score += 15
    cl_score += min(15, overlap * 2.0) # Overlap bonus up to 15 points
    
    suggestions = []
    if not has_greeting:
        suggestions.append("Add a formal greeting at the beginning (e.g., 'Dear Hiring Manager' or 'Dear [Company] Recruiting Team').")
    if not has_signoff:
        suggestions.append("Add a formal sign-off at the end (e.g., 'Sincerely' or 'Best regards') followed by your name.")
    if length_status == "Too Short":
        suggestions.append(f"Your cover letter is very brief ({word_count} words). Aim for at least 200-300 words to explain your motivation.")
    elif length_status == "Too Long":
        suggestions.append(f"Your cover letter is lengthy ({word_count} words). Keep it concise (under 400 words) to respect the recruiter's time.")
    if overlap < 5:
        suggestions.append("Incorporate more key technical terms and skills from the job description to demonstrate alignment.")
        
    return {
        "word_count": word_count,
        "cl_score": int(cl_score),
        "has_greeting": has_greeting,
        "has_signoff": has_signoff,
        "keyword_overlap": overlap,
        "length_status": length_status,
        "suggestions": suggestions
    }

def _analyze_with_gemini(resume_text, job_desc_text, cover_letter_text, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent?key={api_key}"
    
    prompt = (
        "You are an expert Applicant Tracking System (ATS) auditor. Analyze the following candidate's resume "
        "against the provided job description. If a cover letter is provided, analyze it as well.\n\n"
        "### Job Description:\n"
        f"{job_desc_text}\n\n"
        "### Resume:\n"
        f"{resume_text}\n\n"
    )
    if cover_letter_text:
        prompt += (
            "### Cover Letter:\n"
            f"{cover_letter_text}\n\n"
        )
    else:
        prompt += "No cover letter was provided.\n\n"
        
    prompt += (
        "Perform a thorough match analysis:\n"
        "1. Calculate a realistic Match Score (0 to 100) based on how well the candidate's skills and experience align with the job description. Do not be overly generous—scoring should reflect actual alignment.\n"
        "2. Identify technical, soft, and business keywords that are matched, and those that are missing but requested.\n"
        "3. Evaluate the resume structure, word count, metrics (numbers indicating impact), and action verbs.\n"
        "4. If a cover letter is provided, analyze its layout, greeting, signoff, length, and keyword overlap, and score it out of 100.\n"
        "5. Provide actionable suggestions for improving the resume (and cover letter, if provided).\n\n"
        "Provide your output exactly in the requested JSON schema structure."
    )
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "match_score": {"type": "INTEGER"},
            "interview_likelihood": {"type": "STRING"},
            "likelihood_percentage": {"type": "INTEGER"},
            "word_count": {"type": "INTEGER"},
            "metrics_found": {"type": "INTEGER"},
            "action_verbs": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "sections_found": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "sections_missing": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "keywords": {
                "type": "OBJECT",
                "properties": {
                    "matched": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "keyword": {"type": "STRING"},
                                "category": {"type": "STRING"}
                            },
                            "required": ["keyword", "category"]
                        }
                    },
                    "missing": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "keyword": {"type": "STRING"},
                                "category": {"type": "STRING"}
                            },
                            "required": ["keyword", "category"]
                        }
                    },
                    "match_ratio": {"type": "STRING"}
                },
                "required": ["matched", "missing", "match_ratio"]
            },
            "suggestions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "type": {"type": "STRING"},
                        "priority": {"type": "STRING"},
                        "message": {"type": "STRING"}
                    },
                    "required": ["type", "priority", "message"]
                }
            },
            "cover_letter": {
                "type": "OBJECT",
                "properties": {
                    "word_count": {"type": "INTEGER"},
                    "cl_score": {"type": "INTEGER"},
                    "has_greeting": {"type": "BOOLEAN"},
                    "has_signoff": {"type": "BOOLEAN"},
                    "keyword_overlap": {"type": "INTEGER"},
                    "length_status": {"type": "STRING"},
                    "suggestions": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": ["word_count", "cl_score", "has_greeting", "has_signoff", "keyword_overlap", "length_status", "suggestions"]
            }
        },
        "required": [
            "match_score",
            "interview_likelihood",
            "likelihood_percentage",
            "word_count",
            "metrics_found",
            "action_verbs",
            "sections_found",
            "sections_missing",
            "keywords",
            "suggestions"
        ]
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }
    
    req_body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            content_text = res_json['candidates'][0]['content']['parts'][0]['text']
            parsed_analysis = json.loads(content_text)
            parsed_analysis["parser_used"] = "gemini"
            return parsed_analysis
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

def get_ats_analysis(resume_text, job_desc_text, cover_letter_text=None, parser_mode='local'):
    """
    Runs the complete ATS analysis pipeline.
    Combines text cleanups, custom TF-IDF similarity, keyword overlap, structural checks,
    and cover letter checks to build a detailed report.
    """
    if not resume_text or not resume_text.strip():
        return {"error": "Resume text is empty"}
    if not job_desc_text or not job_desc_text.strip():
        return {"error": "Job description is empty"}
        
    if parser_mode == 'gemini':
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            gemini_result = _analyze_with_gemini(resume_text, job_desc_text, cover_letter_text, api_key)
            if gemini_result:
                return gemini_result
            else:
                print("Gemini analysis failed. Falling back to local engine.")
        else:
            print("Gemini API key missing. Falling back to local engine.")
        
    # 1. Tokenize both documents
    resume_tokens = tokenize(resume_text)
    job_tokens = tokenize(job_desc_text)
    
    # 2. Compute Cosine Similarity using TF-IDF
    similarity = calculate_cosine_similarity(resume_tokens, job_tokens)
    
    # 3. Get Matched and Missing Keywords
    matched_kws, missing_kws = get_matching_keywords(resume_text, job_desc_text)
    
    # 4. Keyword Match Percentage
    total_kws = len(matched_kws) + len(missing_kws)
    keyword_match_rate = len(matched_kws) / total_kws if total_kws > 0 else 0.0
    
    # 5. Calculate overall Match Score
    # We balance: 50% Cosine Similarity + 50% Keyword Match Rate
    # Normalize similarity: Cosine similarity is usually low for different texts.
    # A cosine similarity > 0.4 is typically very high. Let's scale similarity.
    scaled_similarity = min(1.0, similarity * 2.2) 
    
    match_score_raw = (scaled_similarity * 40) + (keyword_match_rate * 60)
    match_score = int(min(100, max(0, match_score_raw)))
    
    # 6. Analyze resume layout structure
    struct_metrics = analyze_resume_structure(resume_text)
    
    # 7. Analyze cover letter if provided
    cl_metrics = analyze_cover_letter(cover_letter_text, job_desc_text)
    
    # 8. Calculate Interview Likelihood
    # A mix of match score, structure completeness, and metrics presence.
    likelihood_val = match_score
    if struct_metrics["metrics_count"] >= 3:
        likelihood_val += 5 # bonus for metrics
    if not struct_metrics["missing_headers"]:
        likelihood_val += 5 # bonus for complete sections
    if cl_metrics and cl_metrics["cl_score"] >= 80:
        likelihood_val += 5 # bonus for good cover letter
        
    likelihood_val = min(100, likelihood_val)
    
    if likelihood_val >= 80:
        interview_likelihood = "High Match"
        likelihood_percentage = int(likelihood_val)
    elif likelihood_val >= 55:
        interview_likelihood = "Moderate Match"
        likelihood_percentage = int(likelihood_val)
    else:
        interview_likelihood = "Low Match"
        likelihood_percentage = int(likelihood_val)
        
    # 9. Generate suggestions for improvement
    suggestions = []
    
    # Section Header suggestions
    if struct_metrics["missing_headers"]:
        missing_list = ", ".join([h.capitalize() for h in struct_metrics["missing_headers"]])
        suggestions.append({
            "type": "structure",
            "priority": "High",
            "message": f"Missing critical section headers: **{missing_list}**. Recruiters and ATS scanners look for these labels to parse your document."
        })
        
    # Keyword suggestions
    if missing_kws:
        top_missing = [item["keyword"] for item in missing_kws[:5]]
        missing_str = ", ".join([f"'{k}'" for k in top_missing])
        suggestions.append({
            "type": "keywords",
            "priority": "High",
            "message": f"Incorporate these top missing skills from the job description: **{missing_str}**. Try adding them naturally inside your Projects or Experience bullet points."
        })
        
    # Quantifying impact
    if struct_metrics["metrics_count"] < 3:
        suggestions.append({
            "type": "formatting",
            "priority": "Medium",
            "message": f"Only found {struct_metrics['metrics_count']} metrics/numbers in your experience. Recruiters love seeing quantified results (e.g., 'reduced load time by 30%', 'managed $5k budget'). Add more numbers to prove your impact."
        })
        
    # Word count check
    w_count = struct_metrics["word_count"]
    if w_count < 300:
        suggestions.append({
            "type": "formatting",
            "priority": "Medium",
            "message": f"Your resume is very short ({w_count} words). Expanding on project details, technologies used, and responsibilities can increase keyword matches."
        })
    elif w_count > 1000:
        suggestions.append({
            "type": "formatting",
            "priority": "Low",
            "message": f"Your resume is quite long ({w_count} words). Aim for a concise, high-impact one-page resume (roughly 400-800 words) so recruiters can scan it in 6 seconds."
        })
        
    # Action verbs check
    if len(struct_metrics["action_verbs_found"]) < 3:
        suggestions.append({
            "type": "content",
            "priority": "Low",
            "message": "Start your experience bullet points with strong action verbs (e.g., *designed*, *spearheaded*, *automated*, *optimized*) instead of passive language like 'responsible for'."
        })
        
    res = {
        "match_score": match_score,
        "interview_likelihood": interview_likelihood,
        "likelihood_percentage": likelihood_percentage,
        "word_count": w_count,
        "metrics_found": struct_metrics["metrics_count"],
        "action_verbs": struct_metrics["action_verbs_found"],
        "sections_found": [s.capitalize() for s in struct_metrics["found_headers"]],
        "sections_missing": [s.capitalize() for s in struct_metrics["missing_headers"]],
        "keywords": {
            "matched": matched_kws,
            "missing": missing_kws,
            "match_ratio": f"{len(matched_kws)} / {total_kws}" if total_kws > 0 else "0 / 0"
        },
        "cover_letter": cl_metrics,
        "suggestions": suggestions,
        "parser_used": "local"
    }

    if parser_mode == 'gemini':
        res["suggestions"].insert(0, {
            "type": "system",
            "priority": "High",
            "message": "Notice: Gemini API key is missing or the call failed. Fell back to Local NLP matching."
        })

    return res
