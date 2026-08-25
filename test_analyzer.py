# test_analyzer.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

import unittest
from analyzer import (
    clean_and_normalize,
    tokenize,
    get_ngrams,
    calculate_cosine_similarity,
    get_matching_keywords,
    analyze_resume_structure,
    analyze_cover_letter,
    get_ats_analysis,
    has_spring_framework
)

class TestAnalyzer(unittest.TestCase):

    def test_clean_and_normalize(self):
        self.assertEqual(clean_and_normalize("C++ developer in .NET"), "cpp developer in dotnet")
        self.assertEqual(clean_and_normalize("C# programming"), "csharp programming")
        self.assertEqual(clean_and_normalize("Node.js developer"), "nodejs developer")
        self.assertEqual(clean_and_normalize(""), "")

    def test_tokenize(self):
        text = "Experienced software developer. Skills include Python, JavaScript, and C++."
        tokens = tokenize(text)
        # Should clean, normalize C++ to cpp, and filter stopwords (like 'and', 'include')
        self.assertIn("python", tokens)
        self.assertIn("javascript", tokens)
        self.assertIn("cpp", tokens)
        self.assertNotIn("and", tokens)
        self.assertNotIn("include", tokens)

    def test_get_ngrams(self):
        tokens = ["machine", "learning", "model"]
        bigrams = get_ngrams(tokens, 2)
        self.assertEqual(bigrams, ["machine learning", "learning model"])

    def test_cosine_similarity(self):
        doc1 = tokenize("Python developer with React experience")
        doc2 = tokenize("React developer with Python skills")
        similarity = calculate_cosine_similarity(doc1, doc2)
        self.assertGreater(similarity, 0.5) # Highly similar
        
        doc3 = tokenize("Marketing manager and SEO specialist")
        diff_similarity = calculate_cosine_similarity(doc1, doc3)
        self.assertLess(diff_similarity, 0.2) # Very different

    def test_get_matching_keywords(self):
        job_desc = "Looking for a Python developer with React and communication skills."
        resume = "I am a frontend developer specializing in React and JavaScript. Excellent communication."
        
        matched, missing = get_matching_keywords(resume, job_desc)
        
        # Verify matched skills
        matched_words = [item["keyword"] for item in matched]
        self.assertIn("react", matched_words)
        self.assertIn("communication", matched_words)
        
        # Verify missing skills (Python)
        missing_words = [item["keyword"] for item in missing]
        self.assertIn("python", missing_words)
        
        # Verify categorizations
        for item in matched:
            if item["keyword"] == "react":
                self.assertEqual(item["category"], "Technical")
            if item["keyword"] == "communication":
                self.assertEqual(item["category"], "Soft Skills")

    def test_analyze_resume_structure(self):
        resume = """
        John Doe
        Email: john.doe@example.com
        
        Professional Experience:
        - Led a team of 5 developers to build an e-commerce platform.
        - Optimized API responses, reducing load time by 35%.
        
        Education:
        - BS in Computer Science
        
        Skills:
        Python, React, Git, SQL
        """
        
        struct = analyze_resume_structure(resume)
        self.assertIn("experience", struct["found_headers"])
        self.assertIn("education", struct["found_headers"])
        self.assertIn("skills", struct["found_headers"])
        self.assertNotIn("projects", struct["found_headers"]) # Projects header is missing
        
        self.assertIn("projects", struct["missing_headers"])
        self.assertGreater(struct["metrics_count"], 0) # Should find '35%' and '5'
        self.assertIn("led", struct["action_verbs_found"])
        self.assertIn("optimized", struct["action_verbs_found"])

    def test_analyze_cover_letter(self):
        cl = """
        Dear Hiring Manager,
        
        I am writing to enthusiastically apply for the Python developer position. With over three years of hands-on experience designing, developing, and deploying scalable web applications, I am confident that I can bring significant value to your engineering team.
        
        In my previous role, I worked extensively with Python and React to build responsive frontend interfaces integrated with powerful RESTful APIs. I designed complex SQL database schemas, optimized database queries which improved loading speeds by forty percent, and collaborated in an agile environment with weekly sprint planning and code reviews. Furthermore, my experience includes deploying cloud-native microservices on AWS using Docker, establishing continuous integration and delivery pipelines, and maintaining system health metrics.
        
        I possess strong communication and problem-solving skills, and I am passionate about writing clean, maintainable code. I have a proven track record of collaborating across cross-functional teams to deliver high-quality software solutions that meet business requirements.
        
        I am very excited about the opportunity to discuss my qualifications further and demonstrate how my background aligns with your needs. Thank you for your time and consideration.
        
        Sincerely,
        John Doe
        """
        job = "Python developer with React experience, SQL database design, agile environment, AWS cloud pipelines, and strong communication skills."
        
        cl_analysis = analyze_cover_letter(cl, job)
        self.assertIsNotNone(cl_analysis)
        self.assertTrue(cl_analysis["has_greeting"])
        self.assertTrue(cl_analysis["has_signoff"])
        self.assertEqual(cl_analysis["length_status"], "Good")
        self.assertGreater(cl_analysis["cl_score"], 70)
        self.assertEqual(len(cl_analysis["suggestions"]), 0) # No suggestions needed for a good letter

    def test_fuzzy_matching(self):
        job = "Looking for a developer with python, docker, and PostgreSQL experience."
        resume = "Experienced developers specializing in pyhton, dockers, and postgres."
        
        matched, missing = get_matching_keywords(resume, job)
        matched_words = [item["keyword"] for item in matched]
        
        self.assertIn("python", matched_words)
        self.assertIn("docker", matched_words)
        self.assertIn("postgresql", matched_words)

    def test_get_ats_analysis(self):
        job = "Senior Python Developer with AWS cloud skills."
        resume = "Python Developer with AWS experience. Standard Education and Skills."
        
        result = get_ats_analysis(resume, job)
        self.assertIn("match_score", result)
        self.assertIn("interview_likelihood", result)
        self.assertIn("keywords", result)
        self.assertIn("suggestions", result)
        self.assertGreaterEqual(result["match_score"], 50)

    def test_has_spring_framework(self):
        # Framework cases
        self.assertTrue(has_spring_framework("Looking for a Java developer with Spring Boot experience."))
        self.assertTrue(has_spring_framework("Experience with Spring, Hibernate, and Struts."))
        self.assertTrue(has_spring_framework("We are hiring for our Spring 2025 cohort. Candidates must have Spring Framework experience."))
        self.assertTrue(has_spring_framework("Spring Boot Developer for a Spring 2024 project"))
        
        # Seasonal/academic cases
        self.assertFalse(has_spring_framework("Graduated in Spring 2024."))
        self.assertFalse(has_spring_framework("Spring semester 2023: teaching assistant."))
        self.assertFalse(has_spring_framework("Looking for an intern for the Spring term."))
        self.assertFalse(has_spring_framework("Spring/Summer 2024 co-op"))
        self.assertFalse(has_spring_framework("Hiring a Spring Intern"))

    def test_spring_keyword_matching_and_extraction(self):
        # Case 1: Job description mentions Spring 2024 (seasonal). Spring should NOT be extracted as a keyword.
        job_desc = "We are hiring interns for the Spring 2024 term. Basic knowledge of Python is required."
        resume = "Experienced Python developer."
        
        matched, missing = get_matching_keywords(resume, job_desc)
        matched_words = [item["keyword"] for item in matched]
        missing_words = [item["keyword"] for item in missing]
        
        self.assertNotIn("spring", matched_words)
        self.assertNotIn("spring", missing_words)
        self.assertIn("python", matched_words)

        # Case 2: Job description asks for Spring Boot (framework), but resume only has Spring 2024 (seasonal).
        # Spring should be extracted as a missing keyword.
        job_desc_fw = "We need a Backend Developer with Spring Boot and Java."
        resume_seasonal = "Java developer. Graduated in Spring 2024."
        
        matched_fw, missing_fw = get_matching_keywords(resume_seasonal, job_desc_fw)
        matched_words_fw = [item["keyword"] for item in matched_fw]
        missing_words_fw = [item["keyword"] for item in missing_fw]
        
        self.assertIn("java", matched_words_fw)
        self.assertNotIn("spring", matched_words_fw)
        self.assertIn("spring", missing_words_fw)

        # Case 3: Job description asks for Spring Boot (framework), and resume has Spring Boot (framework).
        # Spring should be extracted as a matched keyword.
        resume_fw = "Java developer with Spring Boot experience."
        matched_match, missing_match = get_matching_keywords(resume_fw, job_desc_fw)
        matched_words_match = [item["keyword"] for item in matched_match]
        missing_words_match = [item["keyword"] for item in missing_match]
        
        self.assertIn("java", matched_words_match)
        self.assertIn("spring", matched_words_match)
        self.assertNotIn("spring", missing_words_match)

    def test_seasonal_calendar_words_fallback(self):
        # Job description with high frequency of seasonal/calendar words and few standard skills.
        # Fallback to high frequency words should NOT extract "summer" or "december" or "semester".
        job_desc = "We have an internship for the summer. The summer is a great summer semester. This summer and december you will work on tasks, tasks, tasks, tasks, tasks."
        resume = "Some candidate resume."
        
        matched, missing = get_matching_keywords(resume, job_desc)
        all_extracted = [item["keyword"] for item in matched] + [item["keyword"] for item in missing]
        
        # 'tasks' should be extracted as fallback, but 'summer', 'december', 'semester' should be ignored
        self.assertIn("tasks", all_extracted)
        self.assertNotIn("summer", all_extracted)
        self.assertNotIn("december", all_extracted)
        self.assertNotIn("semester", all_extracted)

    def test_graduation_dates_ignored(self):
        # Job description with graduation dates and class dates
        job_desc = "Expected Graduation: May 2025. Graduation Date: 12/2026. Class of 2024. Basic knowledge of tasks, tasks, tasks, tasks, tasks."
        resume = "Some candidate resume."
        
        matched, missing = get_matching_keywords(resume, job_desc)
        all_extracted = [item["keyword"] for item in matched] + [item["keyword"] for item in missing]
        
        # 'tasks' should be extracted as fallback, but graduation terms, months, and years should be ignored
        self.assertIn("tasks", all_extracted)
        self.assertNotIn("graduation", all_extracted)
        self.assertNotIn("expected", all_extracted)
        self.assertNotIn("may", all_extracted)
        self.assertNotIn("2025", all_extracted)
        self.assertNotIn("12/2026", all_extracted)
        self.assertNotIn("2026", all_extracted)
        self.assertNotIn("class", all_extracted)
        self.assertNotIn("2024", all_extracted)

if __name__ == "__main__":
    unittest.main()
