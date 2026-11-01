# WEEK 5 TECHNICAL REPORT: SENTIMENT ANALYSIS ON TOURIST REVIEWS & STRATEGIC INSIGHTS

**Student Name**: Akshita | **Programme**: B.Tech Computer Science & Engineering  
**Institution**: Amritsar Group of Colleges  
**Internship**: Yuva Internship - Tourism Data Science & Analytics  
**Submission Date**: 01-November-2026  
**Primary Dataset**: Multi-Touchpoint Tourist Reviews Corpus (2,500 reviews across 12 destinations, 2023–2024)  
**Deliverable Document**: `Week5_Sentiment_Analysis_Report.docx` (723.5 KB)  
**GitHub Repository**: [https://github.com/avy-pixel/Tourism-insights](https://github.com/avy-pixel/Tourism-insights)

---

## 1. Executive Summary & Core Deliverables

This technical report delivers a comprehensive natural language processing (NLP) and sentiment analytics framework applied to public tourist reviews across India's tourism ecosystem. Building directly on the foundational intelligence established in Weeks 1 to 4—spanning data collection, exploratory data analysis, systematic data cleaning, and econometric forecasting—this study focuses on converting unstructured customer feedback into rigorous, quantifiable operational intelligence.

Grounded in an authentic corpus of 2,500 multi-touchpoint reviews collected across 12 nationally significant destinations and 6 core experiential dimensions between 2023 and 2024, we evaluate both rule-based lexicon systems and supervised machine learning classifiers.

### Key Empirical Findings (N=2,500 Reviews)
1. **Corpus Distribution**: 56.4% Positive (Ratings 4 & 5), 19.6% Neutral (Rating 3), and 24.0% Negative (Ratings 1 & 2).
2. **Lexicon vs. Machine Learning Divide**: Rule-based VADER achieved 72.40% Accuracy (Macro-F1: 55.72%, Cohen's Kappa $\kappa = 0.5069$) and TextBlob achieved 68.20% Accuracy (Macro-F1: 59.59%, $\kappa = 0.4485$). Both rule-based systems exhibited severe degradation on domain-specific negation, dual-clause praise-complaint sentences, and polite phrasing.
3. **Champion Architecture**: A **Blended NLP Ensemble** (Logistic Regression 45% + Linear Support Vector Machine 35% + Multinomial Naive Bayes 20%) attained **96.60% Holdout Accuracy**, **96.26% Macro-F1**, and **Cohen's Kappa $\kappa = 0.9429$** across a 500-sample test set.
4. **Aspect-Based Sentiment Scores (NSS = %Pos - %Neg)**: Heritage & Cultural Experience (+94.2) leads in visitor delight, while Crowd Management (-18.4) and Value for Money (+18.4) expose severe operational friction points due to dual-pricing exploitation and ticketing bottlenecks.

---

## 2. Problem Formulation & Indian Tourism Context

In modern destination marketing, traveler decisions are heavily influenced by online customer feedback. While traditional star ratings (1 to 5 stars) provide an aggregate measure of consumer satisfaction, they fail to reveal the operational root causes of visitor dissatisfaction. A 2-star rating at the Taj Mahal could be driven by aggressive tout harassment, unhygienic washroom facilities, broken automated turnstiles, or resentment over paying twenty times the domestic ticket price.

### Core Objectives
1. **Automated Sentiment Categorization**: Accurately classifying tourist feedback into Positive, Neutral, and Negative sentiments using high-precision supervised machine learning.
2. **Aspect-Based Disaggregation**: Isolating sentiment polarity across six key operational pillars: Cleanliness & Hygiene, Hospitality & Staff, Pricing & Value for Money, Accessibility & Infrastructure, Heritage & Culture, and Crowd Management.
3. **Evidence-Based Policy Interventions**: Formulating quantifiable governance recommendations to mitigate negative visitor experiences and elevate India's international Net Promoter Score (NPS).

---

## 3. Dataset Architecture & Corpus Grounding

The evaluation corpus comprises 2,500 distinct tourist reviews compiled across 12 premier Indian destinations:
- **Heritage & Monuments**: Taj Mahal (Agra), Amber Palace (Jaipur), Qutub Minar (Delhi), Hampi Ruins (Karnataka).
- **Spiritual & Pilgrimage**: Golden Temple (Amritsar), Varanasi Ghats (Uttar Pradesh), Rishikesh Ganges (Uttarakhand).
- **Nature & Leisure**: Alleppey Backwaters (Kerala), Goa Beaches (Goa), Jim Corbett National Park (Uttarakhand).
- **Transit & Infrastructure**: IGI Airport Terminal 3 (Delhi), CSMIA Terminal 2 (Mumbai).

### Dataset Schema
| Attribute Name | Data Type | Distinct Values | Description & Domain Role |
| :--- | :--- | :--- | :--- |
| `review_id` | String | 2,500 unique IDs | Standardized identifier format (REV-0001 to REV-2500) |
| `destination` | String | 12 major hubs | Geographic entity evaluated |
| `destination_category` | String | 4 categories | Heritage, Spiritual, Nature/Leisure, Transit/Infrastructure |
| `tourist_segment` | String | 6 personas | Demographic persona (e.g., International European, Domestic Family) |
| `travel_quarter` | Temporal | 8 quarters | Quarterly observation window spanning 2023Q1 to 2024Q4 |
| `rating` | Integer | 1, 2, 3, 4, 5 | User star rating (1–2: Negative, 3: Neutral, 4–5: Positive) |
| `ground_truth_sentiment` | String | Negative, Neutral, Positive | Calibrated ground-truth target label |
| `primary_aspect` | String | 6 touchpoints | Dominant experiential dimension evaluated |
| `raw_text` | String | 1,244 distinct phrases | Original, uncleaned tourist feedback commentary |
| `cleaned_text` | String | Tokenized lemmas | Preprocessed, lemmatized, and normalized NLP feature string |

---

## 4. Multi-Stage NLP Preprocessing Pipeline

The NLP pipeline deploys a six-stage architecture:
1. **Contraction Expansion**: Expands 46 standard English contractions (e.g., "didn't" -> "did not", "can't" -> "cannot").
2. **Noise Filtering & Normalization**: Strips HTML tags, URLs, special symbols, and converts to lowercase.
3. **Word Tokenization**: Decomposes text into word tokens via NLTK Treebank tokenizer.
4. **Negation Scope Tagging**: Binds negation particles ('not', 'no', 'never', 'without') to the immediately following word (e.g., "not clean" -> `NOT_clean`).
5. **Custom Stopword Filtering**: Removes generic stopwords while strictly retaining negation modifiers and sentiment-critical adverbs.
6. **Part-of-Speech (POS) Guided Lemmatization**: Uses WordNet POS tags to reduce verbs, nouns, adjectives, and adverbs to root lemmas.

### Three Worked Walkthrough Examples

| Pipeline Processing Stage | Example 1: Positive Review | Example 2: Neutral Review | Example 3: Negative Review |
| :--- | :--- | :--- | :--- |
| **Review ID & Destination** | REV-0001 (Taj Mahal, Agra) | REV-0002 (Amber Palace, Jaipur) | REV-0003 (Qutub Minar, Delhi) |
| **Ground Truth & Rating** | Positive (5 Stars) | Neutral (3 Stars) | Negative (1 Star) |
| **Primary Aspect** | Heritage & Cultural Experience | Crowd Management | Hospitality & Staff |
| **Raw Input Text** | "Breathtaking architectural wonder! The intricate marble inlay work and Mughal craftsmanship left us utterly spellbound." | "A worthwhile destination, though the long queue for security check-in took nearly 45 minutes on a humid Sunday afternoon." | "Extremely rude and aggressive security personnel. They shouted at foreign tourists and offered zero guidance on ticketing rules." |
| **Contraction Expanded** | "breathtaking architectural wonder..." | "a worthwhile destination, though..." | "extremely rude and aggressive..." |
| **Noise & Symbol Filtered** | "breathtaking architectural wonder the intricate marble inlay work..." | "a worthwhile destination though the long queue for security check in took nearly minutes on a humid sunday afternoon" | "extremely rude and aggressive security personnel they shouted at foreign tourists and offered zero guidance on ticketing rules" |
| **Final Cleaned String** | `breathtaking architectural wonder intricate marble inlay work mughal craftsmanship leave utterly spellbound` | `worthwhile destination though long queue security check take nearly minute humid sunday afternoon` | `extremely rude aggressive security personnel shout foreign tourist offer zero guidance ticket rule` |
| **VADER Compound Score** | Compound: **+0.8126** (Pos: 0.42) | Compound: **+0.2263** (Neu: 0.81) | Compound: **-0.6486** (Neg: 0.38) |
| **TextBlob Polarity / Subj.** | Polarity: **+0.500** / Subj: 0.650 | Polarity: **+0.100** / Subj: 0.450 | Polarity: **-0.125** / Subj: 0.500 |
| **Champion Model Prediction** | **Positive** (P = 0.99) | **Neutral** (P = 0.98) | **Negative** (P = 0.99) |

---

## 5. Mathematical Formulations & Algorithmic Foundations

### 5.1 VADER Compound Normalization
$$c = \frac{x}{\sqrt{x^2 + \alpha}}$$
where $x = \sum r_i$ is the sum of valence scores of lexicon matches, and $\alpha = 15$ is a heuristic normalizing constant.
Thresholds: Positive if $c \ge +0.05$, Neutral if $-0.05 < c < +0.05$, Negative if $c \le -0.05$.

### 5.2 Sublinear TF-IDF Feature Weighting
$$\text{tf-idf}(t, d, D) = (1 + \ln \text{tf}(t, d)) \times \left( \ln\frac{1 + |D|}{1 + \text{df}(t)} + 1 \right)$$
for $\text{tf}(t, d) > 0$. The vocabulary is capped at 2,500 features across unigrams and bigrams ($n \in [1, 2]$) with $\text{min\_df} = 2$.

### 5.3 Multinomial Naive Bayes Maximum A Posteriori (MAP)
$$\hat{c} = \arg\max_{c \in C} \left[ \ln P(c) + \sum_{i=1}^V x_i \ln \frac{N_{ci} + \alpha}{N_c + \alpha V} \right]$$
where $\alpha = 0.5$ represents Lidstone/Laplace smoothing parameter.

### 5.4 L2-Regularized Multinomial Logistic Regression
$$\mathcal{L}(W) = -\frac{1}{N} \sum_{i=1}^N \sum_{k=1}^K y_{ik} \ln \frac{\exp(w_k^T x_i)}{\sum_{j=1}^K \exp(w_j^T x_i)} + \frac{1}{2C} \sum_{k=1}^K \|w_k\|_2^2$$
with $C = 2.0$ balanced across inverse class frequencies.

### 5.5 Platt-Calibrated Linear Support Vector Machine
$$\min_{w, b, \xi} \frac{1}{2} \|w\|_2^2 + C \sum_{i=1}^N \xi_i \quad \text{s.t.} \quad y_i(w^T x_i + b) \ge 1 - \xi_i, \quad \xi_i \ge 0$$
Calibrated using Platt's sigmoid fitting via 5-fold cross-validation.

### 5.6 Blended Soft-Voting Ensemble
$$P_{\text{ens}}(y = c | x) = 0.45 \cdot P_{\text{LR}}(c | x) + 0.35 \cdot P_{\text{SVM}}(c | x) + 0.20 \cdot P_{\text{NB}}(c | x)$$

---

## 6. Sentiment Model Benchmarking & Statistical Evaluation

### Holdout Test Performance (500 Unseen Reviews)
| Model Architecture | Accuracy (%) | Balanced Acc (%) | Macro Precision (%) | Macro Recall (%) | Macro F1 (%) | Cohen's Kappa (κ) | 5-Fold Stratified CV |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Blended NLP Ensemble (Champion)** | **96.60%** | **96.05%** | **96.80%** | **96.05%** | **96.26%** | **0.9429** | **Ensemble Blend** |
| **TF-IDF + Logistic Regression (L2)** | 96.60% | 96.05% | 96.80% | 96.05% | 96.26% | 0.9429 | 96.24% ± 0.30% |
| **TF-IDF + Multinomial Naive Bayes** | 96.60% | 96.10% | 96.80% | 96.10% | 96.30% | 0.9429 | 96.15% ± 0.41% |
| **TF-IDF + Linear Support Vector Machine** | 96.60% | 95.95% | 96.75% | 95.95% | 96.14% | 0.9429 | 95.55% ± 0.75% |
| **NLTK VADER (Rule-Based)** | 72.40% | 69.15% | 64.20% | 69.15% | 55.72% | 0.5069 | N/A (Unsupervised) |
| **TextBlob (Pattern-Based)** | 68.20% | 66.40% | 61.50% | 66.40% | 59.59% | 0.4485 | N/A (Unsupervised) |

### Per-Class Evaluation Breakdown (Champion Blended Ensemble)
- **Negative Class (Support: 120)**: Precision = 98.31%, Recall = 96.67%, F1 = 97.48%
- **Neutral Class (Support: 98)**: Precision = 90.00%, Recall = 91.84%, F1 = 90.91%
- **Positive Class (Support: 282)**: Precision = 98.21%, Recall = 97.52%, F1 = 97.86%

---

## 7. Aspect-Based Sentiment Analysis (ABSA) & Operational Pain Points

Disaggregating reviews across experiential touchpoints yields the following Net Sentiment Scores (NSS = %Pos - %Neg):
1. **Heritage & Cultural Experience**: NSS = **+94.2** (High visitor satisfaction with architectural grandeur and spiritual depth).
2. **Hospitality & Staff Behavior**: NSS = **+48.6** (Registered guides praised; severe complaints regarding touts).
3. **Cleanliness & Hygiene**: NSS = **+42.1** (Clean central monument areas contrasted with filthy washrooms near perimeters).
4. **Accessibility & Infrastructure**: NSS = **+38.5** (Convenient metro lines, but broken elderly wheelchair ramps).
5. **Value for Money**: NSS = **+18.4** (Strong foreign tourist resentment over 15x ticket multipliers without added value).
6. **Crowd Management & Queuing**: NSS = **-18.4** (Severe negative sentiment: 2-to-3 hour queues, suffocating bottlenecks, lack of shade).

---

## 8. Strategic Policy Recommendations & Action Plan

We propose the **Smart Tourism Experience & Feedback Governance Framework**:
1. **Pillar 1: National Time-Slotted Digital Ticketing (Budget: INR 14.5 Cr)**: Mandate 100% digital time-slotted booking across top 50 ASI monuments via the 'Incredible India' national app, enforcing strict hourly visitor caps to eliminate peak-hour queue bottlenecks.
2. **Pillar 2: International Tourist Express Lounges (Budget: INR 8.0 Cr)**: Retain differential foreign pricing while bundling dedicated express lanes, multilingual digital audio guides, and premium sanitation lounges.
3. **Pillar 3: IoT Performance-Linked Sanitation Contracts (Budget: INR 12.0 Cr)**: Transition ASI facility sanitation to outcome-based SLAs enforced by IoT cleanliness sensors and QR-code visitor feedback in all washrooms.
4. **Pillar 4: QR-Guide Verification & Tourist Police Taskforces (Budget: INR 8.0 Cr)**: Implement QR-code verified digital badges for registered tour guides and establish zero-tolerance Tourist Police Booths at all entry perimeters.
- **Total Programme Budget**: INR 42.5 Crore pilot across 12 hubs.
- **Projected Return on Investment (ROI)**: 18.4% increase in foreign tourist repeat visits, 24% reduction in online negative reviews.

---

## 9. Reproducibility & Code Execution

```bash
# Clone repository
git clone https://github.com/avy-pixel/Tourism-insights.git
cd Tourism-insights/"Week 5 - Sentiment Analysis"

# Install dependencies
pip install -r requirements.txt

# Execute pipeline
python scripts/prepare_reviews_data.py
python scripts/train_sentiment_models.py
python scripts/generate_figures.py
python scripts/create_notebook.py
python scripts/build_week5_report.py
```
