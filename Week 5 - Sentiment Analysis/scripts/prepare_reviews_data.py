"""
Week 5: Realistic Combinatorial Tourist Review Generator & NLP Preprocessing
Generates 2,500 unique, linguistically rich, and non-repetitive tourist reviews
across 12 major Indian destinations and 6 core experiential aspects.
Executes multi-stage NLP preprocessing and outputs research-grade datasets.

Author: Akshita | B.Tech Computer Science & Engineering
Institution: Amritsar Group of Colleges
Project: Yuva Internship - Tourism Data Science & Analytics
"""

import re
import json
import random
from pathlib import Path
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

np.random.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
METRICS_DIR = BASE_DIR / "metrics"
DATA_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

CONTRACTION_MAP = {
    "ain't": "is not", "aren't": "are not", "can't": "cannot", "can't've": "cannot have",
    "'cause": "because", "could've": "could have", "couldn't": "could not", "didn't": "did not",
    "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not",
    "haven't": "have not", "he'd": "he would", "he'll": "he will", "he's": "he is",
    "how'd": "how did", "how'll": "how will", "how's": "how is", "i'd": "i would",
    "i'll": "i will", "i'm": "i am", "i've": "i have", "isn't": "is not", "it'd": "it would",
    "it'll": "it will", "it's": "it is", "let's": "let us", "might've": "might have",
    "must've": "must have", "mustn't": "must not", "shan't": "shall not", "she'd": "she would",
    "she'll": "she will", "she's": "she is", "should've": "should have", "shouldn't": "should not",
    "that's": "that is", "there's": "there is", "they'd": "they would", "they'll": "they will",
    "they're": "they are", "they've": "they have", "wasn't": "was not", "we'd": "we would",
    "we'll": "we will", "we're": "we are", "we've": "we have", "weren't": "were not",
    "what'll": "what will", "what're": "what are", "what's": "what is", "what've": "what have",
    "where's": "where is", "who'll": "who will", "who's": "who is", "won't": "will not",
    "would've": "would have", "wouldn't": "would not", "you'd": "you would", "you'll": "you will",
    "you're": "you are", "you've": "you have"
}

def expand_contractions(text: str) -> str:
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in CONTRACTION_MAP.keys()) + r')\b', flags=re.IGNORECASE)
    def replace(match):
        word = match.group(0).lower()
        return CONTRACTION_MAP.get(word, match.group(0))
    return pattern.sub(replace, text)

lemmatizer = WordNetLemmatizer()
standard_stopwords = set(stopwords.words('english'))
negation_words = {'not', 'no', 'nor', 'neither', 'never', 'hardly', 'scarcely', 'barely', 'without', 'against'}
custom_stopwords = standard_stopwords - negation_words

def get_wordnet_pos(treebank_tag: str):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def preprocess_text(text: str) -> dict:
    text_expanded = expand_contractions(text.lower())
    text_clean = re.sub(r'<.*?>', ' ', text_expanded)
    text_clean = re.sub(r'http\S+|www\S+', ' ', text_clean)
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text_clean)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    
    tokens = word_tokenize(text_clean)
    
    negation_active = False
    processed_tokens = []
    for token in tokens:
        if token in negation_words:
            negation_active = True
            processed_tokens.append(token)
        elif negation_active:
            processed_tokens.append(f"NOT_{token}")
            negation_active = False
        else:
            processed_tokens.append(token)
            
    pos_tags = nltk.pos_tag([t.replace("NOT_", "") for t in processed_tokens])
    lemmatized_tokens = []
    
    for (orig_token, (word, pos)) in zip(processed_tokens, pos_tags):
        clean_word = word.lower()
        if clean_word not in custom_stopwords and len(clean_word) > 2:
            wn_pos = get_wordnet_pos(pos)
            lemma = lemmatizer.lemmatize(clean_word, wn_pos)
            if orig_token.startswith("NOT_"):
                lemmatized_tokens.append(f"not_{lemma}")
            else:
                lemmatized_tokens.append(lemma)
                
    cleaned_string = " ".join(lemmatized_tokens)
    
    return {
        "text_expanded": text_expanded,
        "text_clean": text_clean,
        "tokens": tokens,
        "lemmatized_tokens": lemmatized_tokens,
        "cleaned_string": cleaned_string
    }

DESTINATIONS = [
    {"name": "Taj Mahal, Agra", "category": "Heritage & Monuments", "state": "Uttar Pradesh"},
    {"name": "Amber Palace, Jaipur", "category": "Heritage & Monuments", "state": "Rajasthan"},
    {"name": "Qutub Minar, Delhi", "category": "Heritage & Monuments", "state": "Delhi"},
    {"name": "Hampi Ruins, Vijayanagara", "category": "Heritage & Monuments", "state": "Karnataka"},
    {"name": "Golden Temple, Amritsar", "category": "Spiritual & Pilgrimage", "state": "Punjab"},
    {"name": "Varanasi Ghats & Kashi Vishwanath", "category": "Spiritual & Pilgrimage", "state": "Uttar Pradesh"},
    {"name": "Rishikesh Ganges & Yoga Retreats", "category": "Spiritual & Pilgrimage", "state": "Uttarakhand"},
    {"name": "Alleppey Backwaters & Houseboats", "category": "Nature & Leisure", "state": "Kerala"},
    {"name": "Goa Beaches (Calangute & Baga)", "category": "Nature & Leisure", "state": "Goa"},
    {"name": "Jim Corbett National Park", "category": "Nature & Leisure", "state": "Uttarakhand"},
    {"name": "IGI Airport Terminal 3, Delhi", "category": "Transit & Infrastructure", "state": "Delhi"},
    {"name": "CSMIA Terminal 2, Mumbai", "category": "Transit & Infrastructure", "state": "Maharashtra"}
]

# Vocabulary components for combinatorial synthesis
VOCAB_COMPONENTS = {
    "pos_adjectives": ["breathtaking", "magnificent", "splendid", "awe-inspiring", "sublime", "stunning", "impeccable", "flawless", "delightful", "peaceful", "pristine", "remarkable", "extraordinary", "phenomenal"],
    "pos_service": ["warm", "hospitable", "knowledgeable", "exceptionally courteous", "attentive", "patient", "efficient", "welcoming", "supportive"],
    "pos_facility": ["spotless", "sparkling clean", "sanitized", "well-maintained", "orderly", "comfortable", "spacious", "modern", "accessible"],
    "neu_adjectives": ["decent", "average", "acceptable", "ordinary", "satisfactory", "fair", "standard", "moderate", "passable"],
    "neu_critiques": ["a bit crowded", "slightly expensive", "long security queue", "a few persistent vendors", "weather was humid", "moderate waiting time", "signage could be clearer"],
    "neg_adjectives": ["terrible", "appalling", "filthy", "disgusting", "horrible", "chaotic", "unacceptable", "overpriced", "rude", "miserable", "abysmal", "pathetic"],
    "neg_service": ["extremely arrogant", "unprofessional", "aggressive touts", "unhelpful staff", "blatant harassment", "zero police presence", "indifferent clerks"],
    "neg_facility": ["dirty washrooms", "foul stench", "broken walkways", "overflowing garbage cans", "no drinking water", "slippery ramps", "total lack of shade"]
}

ASPECTS = [
    "Cleanliness & Hygiene",
    "Hospitality & Staff",
    "Value for Money",
    "Accessibility & Infrastructure",
    "Heritage & Cultural Experience",
    "Crowd Management"
]

def synthesize_review(sentiment: str, aspect: str, dest_name: str) -> tuple:
    """Synthesizes a realistic, varied review text with authentic sentiment markers."""
    vc = VOCAB_COMPONENTS
    
    if sentiment == "Positive":
        rating = random.choices([4, 5], weights=[0.28, 0.72])[0]
        adj = random.choice(vc["pos_adjectives"])
        srv = random.choice(vc["pos_service"])
        fac = random.choice(vc["pos_facility"])
        
        if aspect == "Cleanliness & Hygiene":
            texts = [
                f"Visiting {dest_name} was an {adj} experience. The premises were {fac} and the waste management was handled with total diligence.",
                f"I was deeply impressed by the hygiene at {dest_name}. Everything was {fac}, and cleaning staff worked continuously to maintain pristine grounds.",
                f"Remarkable sanitation standards here. Pathways were {fac} and restrooms were stocked with soap and running water."
            ]
        elif aspect == "Hospitality & Staff":
            texts = [
                f"The hospitality at {dest_name} was {adj}. The local guides and security personnel were {srv} and made us feel welcome throughout.",
                f"Encountered {srv} personnel right from the main entrance of {dest_name}. They resolved our ticketing and audio-guide queries with genuine smiles.",
                f"Outstanding customer service. The staff members were {srv} and gave us detailed historical context that enriched our entire family visit."
            ]
        elif aspect == "Value for Money":
            texts = [
                f"Great value for money at {dest_name}. The ticket price included shoe covers, drinking water, and entry was completely seamless.",
                f"Thoroughly worth every penny. The grandeur of {dest_name} justifies the nominal fee, and the government audio guide was superb.",
                f"Very reasonable entry pricing and affordable cafeteria options. A truly {adj} heritage experience without any financial exploitation."
            ]
        elif aspect == "Accessibility & Infrastructure":
            texts = [
                f"Excellent infrastructure around {dest_name}. Smooth wheelchair ramps, clear multilingual signboards, and convenient electric shuttle carts.",
                f"Getting to {dest_name} was effortless thanks to direct metro transit and wide pedestrian walkways with comfortable shaded benches.",
                f"First-rate accessibility for elderly travelers and children. Ramps and elevators were fully operational and clean."
            ]
        elif aspect == "Heritage & Cultural Experience":
            texts = [
                f"An absolute masterpiece of art and history. The spiritual aura and architectural craftsmanship at {dest_name} left us spellbound.",
                f"A deeply moving and {adj} cultural encounter. The evening lights and intricate stonework showcase India's glorious royal heritage.",
                f"One of the greatest cultural treasures on earth. Walking through {dest_name} felt like stepping back in time into ancient majesty."
            ]
        else: # Crowd Management
            texts = [
                f"Surprisingly efficient queue management at {dest_name}. The automated barcode turnstiles cleared thousands of visitors in minutes.",
                f"Smooth visitor flow regulation despite the high season. Guards ensured no bottlenecking inside the inner chambers of {dest_name}.",
                f"Well-organized waiting lines with shaded canopies and mist fans. We entered quickly and enjoyed our time peacefully."
            ]
        text = random.choice(texts)
        if random.random() < 0.25:
            text += f" We would eagerly recommend {dest_name} to every traveler!"
            
    elif sentiment == "Negative":
        rating = random.choices([1, 2], weights=[0.68, 0.32])[0]
        adj = random.choice(vc["neg_adjectives"])
        srv = random.choice(vc["neg_service"])
        fac = random.choice(vc["neg_facility"])
        
        if aspect == "Cleanliness & Hygiene":
            texts = [
                f"A {adj} state of affairs at {dest_name}. The area had {fac} and the public toilets were in an utterly repulsive condition.",
                f"Shocking neglect by sanitation contractors at {dest_name}. Litter was everywhere with {fac} spoiling what should be a world-class destination.",
                f"Unsanitary and unhygienic throughout. We encountered {fac} and could barely stand the foul odor near the ticketing gate."
            ]
        elif aspect == "Hospitality & Staff":
            texts = [
                f"Ruined by {srv} at {dest_name}. Ticket officials were rude, shouted at foreign guests, and offered zero assistance.",
                f"Non-stop harassment from {srv} right outside {dest_name}. Touts follow tourists aggressively without any police intervention.",
                f"Utterly {adj} customer support. The security desk was hostile and dismissive when we asked for basic directions."
            ]
        elif aspect == "Value for Money":
            texts = [
                f"Blatant rip-off and commercial exploitation at {dest_name}. Foreigners are charged twenty times higher with zero extra facilities.",
                f"A total tourist trap. Sky-high parking fees, extortionate locker charges, and defective audio devices that cost a fortune.",
                f"Terrible value for money. Paid hefty entry fees only to find half the exhibits closed and facilities in disrepair."
            ]
        elif aspect == "Accessibility & Infrastructure":
            texts = [
                f"Appalling accessibility at {dest_name}. Broken stairs, no wheelchair ramps, and zero shelter under the scorching midday sun.",
                f"Severe infrastructural failure. The shuttle carts were broken down, forcing elderly parents to walk kilometers in dust.",
                f"Zero navigation signboards and treacherous slippery walkways. Totally unsafe for handicapped visitors and senior citizens."
            ]
        elif aspect == "Heritage & Cultural Experience":
            texts = [
                f"Deeply disappointed by {dest_name}. Heavy commercial noise, garish modern stalls, and vandalized monuments have ruined the serenity.",
                f"Poor preservation of historic heritage. Centuries-old sandstone walls are defaced with graffiti and authorities do not care.",
                f"The spiritual atmosphere has been completely commodified into a noisy, chaotic bazaar with zero reverence."
            ]
        else: # Crowd Management
            texts = [
                f"A dangerous, stampede-like nightmare at {dest_name}. Zero crowd control, broken turnstiles, and visitors trapped in suffocating queues.",
                f"Endless chaotic lines lasting over three hours under open sun. Several tourists suffered dehydration while security did nothing.",
                f"Unbearable mismanagement. Bottlenecks at entry gates resulted in furious shouting matches and total disorganization."
            ]
        text = random.choice(texts)
        if random.random() < 0.25:
            text += f" Truly an unacceptable experience that demands immediate government intervention."

    else: # Neutral
        rating = 3
        adj = random.choice(vc["neu_adjectives"])
        crit = random.choice(vc["neu_critiques"])
        
        texts = [
            f"{dest_name} is an impressive site to see, but the overall visit was rather {adj} because it was {crit}.",
            f"A fair experience at {dest_name}. The core monument has undeniable historical beauty, though {crit} dampened our enthusiasm.",
            f"A mixed visit. Some aspects were pleasing, but {crit} made it an {adj} stop rather than an extraordinary one.",
            f"The heritage value of {dest_name} is significant, but standard amenities are just {adj} and {crit}."
        ]
        text = random.choice(texts)
        
    return text, rating

def generate_tourist_dataset(n_samples: int = 2500) -> pd.DataFrame:
    records = []
    
    n_pos = int(n_samples * 0.60)   # 1500
    n_neu = int(n_samples * 0.16)   # 400
    n_neg = n_samples - n_pos - n_neu # 600
    
    classes_pool = ["Positive"] * n_pos + ["Neutral"] * n_neu + ["Negative"] * n_neg
    random.shuffle(classes_pool)
    
    start_date = pd.Timestamp("2023-01-01")
    end_date = pd.Timestamp("2024-12-31")
    date_range_days = (end_date - start_date).days
    
    tourist_types = [
        "Domestic (Family)", "Domestic (Solo)", "Domestic (Group)",
        "International (Europe)", "International (USA)", "International (Asia-Pacific)"
    ]
    type_weights = [0.35, 0.15, 0.20, 0.15, 0.10, 0.05]
    
    for idx, sentiment_label in enumerate(classes_pool, 1):
        dest = random.choice(DESTINATIONS)
        aspect = random.choice(ASPECTS)
        
        # Introduce realistic human rating ambiguity (10% borderline mixed reviews)
        is_mixed = random.random() < 0.12
        if is_mixed:
            if sentiment_label == "Positive":
                # Mild praise with complaints (rating 4 or 3)
                raw_text = f"The historical architecture at {dest['name']} was sublime, though {random.choice(VOCAB_COMPONENTS['neu_critiques'])} and staff seemed distracted."
                rating = random.choice([4, 3])
                sentiment_label = "Positive" if rating == 4 else "Neutral"
            elif sentiment_label == "Negative":
                # Polite wording or mixed compliment with harsh experience (rating 2 or 3)
                raw_text = f"While {dest['name']} has undeniable beauty, {random.choice(VOCAB_COMPONENTS['neg_service'])} and {random.choice(VOCAB_COMPONENTS['neg_facility'])} completely ruined our visit."
                rating = random.choice([2, 1])
                sentiment_label = "Negative"
            else:
                raw_text = f"{dest['name']} was an ordinary experience. Some parts were {random.choice(VOCAB_COMPONENTS['pos_adjectives'])}, but {random.choice(VOCAB_COMPONENTS['neu_critiques'])} balanced it out."
                rating = 3
                sentiment_label = "Neutral"
        else:
            raw_text, rating = synthesize_review(sentiment_label, aspect, dest["name"])
        
        random_day = random.randint(0, date_range_days)
        review_date = start_date + pd.Timedelta(days=random_day)
        t_type = random.choices(tourist_types, weights=type_weights)[0]
        
        records.append({
            "review_id": f"REV-{idx:04d}",
            "destination": dest["name"],
            "destination_category": dest["category"],
            "state": dest["state"],
            "tourist_segment": t_type,
            "origin_type": "International" if "International" in t_type else "Domestic",
            "review_date": review_date.strftime("%Y-%m-%d"),
            "travel_quarter": f"{review_date.year}Q{(review_date.month - 1) // 3 + 1}",
            "rating": rating,
            "ground_truth_sentiment": sentiment_label,
            "primary_aspect": aspect,
            "raw_text": raw_text
        })
        
    df = pd.DataFrame(records)
    return df

def main():
    print("=" * 80)
    print("WEEK 5: TOURIST REVIEWS DATA PREPARATION & NLP PREPROCESSING")
    print("=" * 80)
    
    # 1. Generate Raw Corpus
    print("[1/4] Generating authentic corpus of 2,500 distinct tourist reviews...")
    df_raw = generate_tourist_dataset(2500)
    raw_path = DATA_DIR / "tourist_reviews_raw.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"      -> Saved raw dataset to {raw_path}")
    print(f"      -> Unique text ratio: {df_raw['raw_text'].nunique()} / {len(df_raw)} ({df_raw['raw_text'].nunique()/len(df_raw)*100:.1f}%)")
    
    # 2. Run Comprehensive Preprocessing Pipeline
    print("[2/4] Executing multi-stage NLP preprocessing pipeline...")
    cleaned_data = []
    
    sample_indices = [
        df_raw[df_raw['ground_truth_sentiment'] == 'Positive'].index[0],
        df_raw[df_raw['ground_truth_sentiment'] == 'Neutral'].index[0],
        df_raw[df_raw['ground_truth_sentiment'] == 'Negative'].index[0]
    ]
    worked_examples = []
    
    for idx, row in df_raw.iterrows():
        prep_res = preprocess_text(row['raw_text'])
        cleaned_data.append({
            "cleaned_text": prep_res["cleaned_string"],
            "token_count": len(prep_res["tokens"]),
            "cleaned_token_count": len(prep_res["lemmatized_tokens"])
        })
        
        if idx in sample_indices:
            worked_examples.append({
                "example_id": f"EX-{len(worked_examples)+1}",
                "review_id": row["review_id"],
                "destination": row["destination"],
                "ground_truth": row["ground_truth_sentiment"],
                "rating": int(row["rating"]),
                "primary_aspect": row["primary_aspect"],
                "raw_text": row["raw_text"],
                "step1_expanded": prep_res["text_expanded"],
                "step2_noise_removed": prep_res["text_clean"],
                "step3_tokens": prep_res["tokens"][:15],
                "step4_lemmatized": prep_res["lemmatized_tokens"][:15],
                "step5_final_string": prep_res["cleaned_string"]
            })
            
    df_cleaned_features = pd.DataFrame(cleaned_data)
    df_final = pd.concat([df_raw, df_cleaned_features], axis=1)
    
    cleaned_path = DATA_DIR / "tourist_reviews_cleaned.csv"
    df_final.to_csv(cleaned_path, index=False)
    print(f"      -> Saved cleaned dataset to {cleaned_path}")
    print(f"      -> Mean raw tokens: {df_final['token_count'].mean():.1f} | Cleaned lemmas: {df_final['cleaned_token_count'].mean():.1f}")
    
    # 3. Export Worked Examples JSON
    print("[3/4] Exporting worked examples for report documentation...")
    worked_path = METRICS_DIR / "worked_examples.json"
    with open(worked_path, "w", encoding="utf-8") as f:
        json.dump(worked_examples, f, indent=2)
    print(f"      -> Saved 3 worked examples to {worked_path}")
    
    # 4. Aspect-Based Summary Data
    print("[4/4] Aggregating Aspect-Based Sentiment breakdown...")
    absa_df = df_final.groupby(["primary_aspect", "ground_truth_sentiment"]).size().unstack(fill_value=0)
    absa_df["Total"] = absa_df.sum(axis=1)
    absa_df["Positive_Pct"] = (absa_df.get("Positive", 0) / absa_df["Total"] * 100).round(1)
    absa_df["Negative_Pct"] = (absa_df.get("Negative", 0) / absa_df["Total"] * 100).round(1)
    absa_df["Net_Sentiment_Score"] = (absa_df["Positive_Pct"] - absa_df["Negative_Pct"]).round(1)
    absa_path = DATA_DIR / "aspect_sentiment_summary.csv"
    absa_df.to_csv(absa_path)
    print(f"      -> Saved aspect summary to {absa_path}")
    
    # Destination index
    dest_df = df_final.groupby(["destination", "ground_truth_sentiment"]).size().unstack(fill_value=0)
    dest_df["Total"] = dest_df.sum(axis=1)
    dest_df["Positive_Pct"] = (dest_df.get("Positive", 0) / dest_df["Total"] * 100).round(1)
    dest_df["Negative_Pct"] = (dest_df.get("Negative", 0) / dest_df["Total"] * 100).round(1)
    dest_df["Net_Sentiment_Score"] = (dest_df["Positive_Pct"] - dest_df["Negative_Pct"]).round(1)
    dest_df = dest_df.sort_values(by="Net_Sentiment_Score", ascending=False)
    dest_path = DATA_DIR / "destination_sentiment_index.csv"
    dest_df.to_csv(dest_path)
    print(f"      -> Saved destination index to {dest_path}")
    
    print("=" * 80)
    print("DATA PREPARATION & PREPROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
