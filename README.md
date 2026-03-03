# Job Resume Matching Project

# Problem
Matching the best profiles to a job description may be a difficult and time-consuming task.
In fact, the traditional way that recruiters are using to select candidates doesn't take into consideration all important details. Recruiters have to screen all the applications manually and then calculate the similarity in an efficient way.

# Solution
<p align="center">
  <img src="./backend/Resources/Project documentation/ai in recruitement.png" width="650" title="AI in recruitment" alt="benefits of AI in recruitment">
 </p>

The idea is to calculate the similarity between the resume and the job description and then return the resumes with the highest similarity score.

## 1st step: information retrieval
  Information Extraction is the task of automatically extracting structured information such as entities, relationships between entities, and attributes describing
entities from unstructured sources. Our system uses spacy PhraseMatcher to extract the information from job descriptions.
We prepared a dictionary that has all education degrees categories, all majors and skills categories related to computer engineering field. We fed that dictionary to the Spacy rule-based PhraseMatcher in order to detect and recognize entities in our job description.
The job information extraction would look like:

<p align="center">
  <img src="./backend/Resources/Project documentation/Job entities example1.png" width="700" title="Job information extraction example" alt="Job information extraction example">
</p>
  
Our structured job descriptions dataset :

<p align="center">
  <img src="./backend/Resources/Project documentation/Job data.png" width="650" title="Job descriptions dataset" alt="Job descriptions dataset">
 </p>

## 2nd step: Matching rules
  We implemented matching rules to calculate the similarity between the resume and the job description. Those matching rules don't only use simple keywords matching but also ontology matching techniques.
 
  #### * Education section matching rules
  <p align="center">
  <img src="./backend/Resources/Project documentation/Education rules.png" width="650" title="Education matching rule" alt="Education matching rule">
  </p>
  
  #### * Majors section matching rules
  <p align="center">
  <img src="./backend/Resources/Project documentation/Majors rules.png" width="600" title="Majors matching rule" alt="Majors matching rule">
  </p>
  
  #### * Skills section matching rules
  
  
  In this part, we will use semantic similarity-based approach to match resumes' skills and jobs' skills.
  Semantic similarity approach is the task of searching for documents or sentences (resumes) which contain semantically similar content to a search document           (the job description).
  
  We tried different pre-trained models to embed our words ('all-mpnet-base-v2', 'paraphrase-MiniLM-L6-v2', 'gpt3','all-MiniLM-L12-v1','all-roberta-large-v1','bert-base-nli-mean-tokens').
  Embeddings are a key part of modern NLP, they encode the meaning of words or other linguistic units into vectors of numbers.

  The steps that we followed later on to calculate the similarity between the job and the resume with each model:
  
  1. We derive semantically meaningful word embeddings using the different models mentioned above

  2. We compare those embeddings with cosine similarity to find the nearest resumes to the job description
     Cosine similarity is defined as the inner product of two vectors divided by the product of their length. Cosine similarity is defined as:
     <p align="center">
    <img src="./backend/Resources/Project documentation/cosine similarity.png" width="650" title="cosine similarity" alt="cosine similarity">
     </p>
     where vectors a and b have the same number of dimensions N. Cosine similarity can be used to compare similarity between document vectors.
          
   We tried that approach on skills words of 15 resumes and 5 jobs :
   The resumes information were extracted by a colleague and the jobs were extracted from a public dataset on Kaggle. 
   
   * Jobs:
   <p align="center">
    <img src="./backend/Resources/Project documentation/jobs.png" width="650" title="jobs_examples" alt="Jobs_examples">
    </p>
    
   * Resumes:
   <p align="center">
    <img src="./backend/Resources/Project documentation/resumes.png" width="650" title="resumes_examples" alt="Resumes_examples">
    </p>
         
   These are some of the scores' results:
   <p align="center">
    <img src="./backend/Resources/Project documentation/matching_results.png" width="650" title="matching_results" alt="matching_results">
    </p>
    
   These are the ranks of resumes for each job:
   <p align="center">
    <img src="./backend/Resources/Project documentation/ranking_results.png" width="650" title="ranking_results" alt="ranking_results">
    </p>
            
            
            
   Evaluation:
   
   We used precision @k metric to evaluate our models' results comparing to manually annotated dataset. Precision at k is the proportion of recommended items in the top-k set that are relevant. In our case k is 15.
   These are the results for each job and model:
   <p align="center">
    <img src="./backend/Resources/Project documentation/precision_results.png" width="650" title="precision_result" alt="precision_results">
    </p>
    
    
   The total precision for each model on 5 jobs:
   <p align="center">
    <img src="./backend/Resources/Project documentation/final_results.png" width="650" title="final_result" alt="final_results">
    </p>
   

  <p>Visit <a href="https://github.com/amiradridi/Job-Resume-Matching/blob/master/services/Models%20evaluation.ipynb">this notebook</a> for the full code of the semantic similarity approach.</p>
  We have chosen 'bert-base-nli-mean-tokens' as skills matching model for its high precision.

  

 
* 3rd step: 
  We Calculated the final similarity score (the mean of skills matching score, degrees matching score and majors matching score) and returned the resumes with the highest similarity score.
  
  
 ## Project summary
 
 1. We retrieved information from the job description using Spacy rule-based PhraseMatcher
 2. We implemented matching rules for the degrees' levels and the acceptable majors
 3. We compared between 6 powerful word embedding models to generate the skills matching scores and we chose 'bert-base-nli-mean-tokens' for its high precision

## Modular AI Resume Skill Gap Analyzer (Extension)

The project now includes a modular skill-gap analysis pipeline that extends (and does not replace) the existing semantic similarity flow.

### New modules

- `backend/services/skill_extractor.py`
  - Explicitly extracts skills from resume and job description text (or accepts pre-extracted skill lists).
- `backend/services/normalizer.py`
  - Normalizes skill variants (e.g. `ml` -> `machine learning`, `pytorch experience` -> `pytorch`) with lowercase + lemmatization-aware cleanup.
- `backend/services/matcher.py`
  - Uses `sentence-transformers` to compute semantic similarity between each job skill and all resume skills.
  - Returns best match per job skill and applies a configurable threshold (default: `0.7`).
- `backend/services/scorer.py`
  - Categorizes job skills into `core`, `supporting`, `optional` with configurable weights (default: `5/3/1`).
  - Computes weighted readiness score:
    - `ReadinessScore = (Sum of MatchedSkillWeight × SimilarityScore) / TotalWeight × 100`
- `backend/services/explainability.py`
  - Builds detailed JSON explainability output, missing-skill impact, and human-readable recommendations.

### New API endpoints

- `POST /skill_gap_analyzer`
  - Run the modular analyzer on raw text or explicit skill lists.

## Frontend (Next.js + React)

A separate frontend app is available in [frontend](frontend).

### Run locally

1. Backend (FastAPI):
  - `cd backend`
  - `uvicorn main:app --host 0.0.0.0 --port 8000`
2. Frontend (Next.js):
  - `cd frontend`
  - Copy `.env.example` to `.env.local`
  - Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL
  - `npm install`
  - `npm run dev`

### Deploy split architecture

- Deploy backend (`backend/main.py`) on Render.
- Deploy frontend (`frontend`) on Vercel.
- Configure Vercel environment variable:
  - `NEXT_PUBLIC_API_BASE_URL=https://<your-render-backend-url>`

### Example request (`POST /skill_gap_analyzer`)

```json
{
  "resume_skills": ["PyTorch experience", "ML", "Python", "SQL"],
  "job_skills": ["Machine Learning", "PyTorch", "Python", "Docker"],
  "job_skill_categories": {
    "machine learning": "core",
    "pytorch": "core",
    "python": "supporting",
    "docker": "optional"
  },
  "category_weights": {
    "core": 5,
    "supporting": 3,
    "optional": 1
  },
  "similarity_threshold": 0.7
}
```

### Response highlights

- normalized skill lists
- per-skill best semantic matches
- weighted readiness score
- detailed explainability JSON with:
  - matched/missing skills
  - similarity scores
  - weight contributions
  - missing core/supporting skill gaps
  - recommendations

 ## References
 
 <p><a href="https://arxiv.org/abs/1908.10084">Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks paper</a></p>
 <p><a href="https://www.sbert.net/docs/pretrained_models.html">Sbert pretrained models official documentation</a></p>
 <p><a href="https://pypi.org/project/sentence-transformers/0.3.2/">Sentence embeddings documentation</a></p>


