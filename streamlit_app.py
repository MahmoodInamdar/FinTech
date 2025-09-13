import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import google.generativeai as genai
from io import StringIO
import warnings
import gc
from typing import Optional, Dict, Any
import time
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings('ignore')

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCZ3XGzKPYWP8cjWWwVv2AzmuE7a2Arw50"
genai.configure(api_key=GEMINI_API_KEY)

# Page configuration with optimizations for large files
st.set_page_config(
    page_title="🚀 DataViz Pro - Advanced Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "DataViz Pro v2.1 - Enterprise Analytics Platform"
    }
)

# Configure Streamlit for better performance with large files
if 'file_processing_config' not in st.session_state:
    st.session_state.file_processing_config = {
        'chunk_size': 10000,  # Process data in chunks
        'max_sample_size': 100000,  # Maximum rows for visualization
        'enable_caching': True,
        'memory_threshold': 500  # MB threshold for optimization
    }

# Language and Theme Support with file persistence
if "language" not in st.session_state:
    st.session_state.language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "Modern Blue"
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "response_length" not in st.session_state:
    st.session_state.response_length = "Concise"

# Language translations
LANGUAGES = {
    "English": {
        "title": "🚀 DataViz Pro - Advanced Analytics Dashboard",
        "upload": "📁 Upload Your Data",
        "file_upload": "Choose a CSV file",
        "overview": "📊 Overview",
        "visualizations": "📈 Visualizations", 
        "data_explorer": "🔍 Data Explorer",
        "ai_assistant": "🤖 AI Assistant",
        "summary": "📋 Summary",
        "chat_placeholder": "Ask a question about your data...",
        "ask_ai": "🚀 Ask AI Assistant"
    },
    "हिंदी": {
        "title": "🚀 डेटाविज़ प्रो - उन्नत विश्लेषणात्मक डैशबोर्ड",
        "upload": "📁 अपना डेटा अपलोड करें",
        "file_upload": "CSV फ़ाइल चुनें",
        "overview": "📊 अवलोकन",
        "visualizations": "📈 दृश्यीकरण",
        "data_explorer": "🔍 डेटा एक्सप्लोरर",
        "ai_assistant": "🤖 AI सहायक",
        "summary": "📋 सारांश",
        "chat_placeholder": "अपने डेटा के बारे में प्रश्न पूछें...",
        "ask_ai": "🚀 AI सहायक से पूछें"
    },
    "தமிழ்": {
        "title": "🚀 டேட்டாவிஸ் ப்ரோ - மேம்பட்ட பகுப்பாய்வு டாஷ்போர்டு",
        "upload": "📁 உங்கள் தரவைப் பதிவேற்றவும்",
        "file_upload": "CSV கோப்பைத் தேர்ந்தெடுக்கவும்",
        "overview": "📊 மேலோட்டம்",
        "visualizations": "📈 காட்சிப்படுத்தல்கள்",
        "data_explorer": "🔍 டேட்டா எக்ஸ்ப்ளோரர்",
        "ai_assistant": "🤖 AI உதவியாளர்",
        "summary": "📋 சுருக்கம்",
        "chat_placeholder": "உங்கள் தரவைப் பற்றி கேள்வி கேளுங்கள்...",
        "ask_ai": "🚀 AI உதவியாளரிடம் கேளுங்கள்"
    },
    "বাংলা": {
        "title": "🚀 ডেটাভিজ প্রো - উন্নত বিশ্লেষণ ড্যাশবোর্ড",
        "upload": "📁 আপনার ডেটা আপলোড করুন",
        "file_upload": "CSV ফাইল নির্বাচন করুন",
        "overview": "📊 সংক্ষিপ্ত বিবরণ",
        "visualizations": "📈 ভিজ্যুয়ালাইজেশন",
        "data_explorer": "🔍 ডেটা এক্সপ্লোরার",
        "ai_assistant": "🤖 AI সহায়ক",
        "summary": "📋 সারাংশ",
        "chat_placeholder": "আপনার ডেটা সম্পর্কে প্রশ্ন করুন...",
        "ask_ai": "🚀 AI সহায়ককে জিজ্ঞাসা করুন"
    },
    "ગુજરાતી": {
        "title": "🚀 ડેટાવિઝ પ્રો - અદ્યતન વિશ્લેષણાત્મક ડેશબોર્ડ",
        "upload": "📁 તમારો ડેટા અપલોડ કરો",
        "file_upload": "CSV ફાઇલ પસંદ કરો",
        "overview": "📊 વિહંગાવલોકન",
        "visualizations": "📈 વિઝ્યુઅલાઇઝેશન",
        "data_explorer": "🔍 ડેટા એક્સપ્લોરર",
        "ai_assistant": "🤖 AI સહાયક",
        "summary": "📋 સારાંશ",
        "chat_placeholder": "તમારા ડેટા વિશે પ્રશ્ન પૂછો...",
        "ask_ai": "🚀 AI સહાયકને પૂછો"
    },
    "తెలుగు": {
        "title": "🚀 డేటావిజ్ ప్రో - అధునాతన విశ్లేషణ డాష్‌బోర్డ్",
        "upload": "📁 మీ డేటాను అప్‌లోడ్ చేయండి",
        "file_upload": "CSV ఫైల్‌ను ఎంచుకోండి",
        "overview": "📊 అవలోకనం",
        "visualizations": "📈 విజువలైజేషన్లు",
        "data_explorer": "🔍 డేటా ఎక్స్‌ప్లోరర్",
        "ai_assistant": "🤖 AI సహాయకుడు",
        "summary": "📋 సారాంశం",
        "chat_placeholder": "మీ డేటా గురించి ప్రశ్న అడగండి...",
        "ask_ai": "🚀 AI సహాయకుడిని అడగండి"
    },
    "मराठी": {
        "title": "🚀 डेटाविझ प्रो - प्रगत विश्लेषण डॅशबोर्ड",
        "upload": "📁 तुमचा डेटा अपलोड करा",
        "file_upload": "CSV फाइल निवडा",
        "overview": "📊 अवलोकन",
        "visualizations": "📈 व्हिज्युअलायझेशन",
        "data_explorer": "🔍 डेटा एक्सप्लोरर",
        "ai_assistant": "🤖 AI सहाय्यक",
        "summary": "📋 सारांश",
        "chat_placeholder": "तुमच्या डेटाबद्दल प्रश्न विचारा...",
        "ask_ai": "🚀 AI सहाय्यकाला विचारा"
    },
    "ಕನ್ನಡ": {
        "title": "🚀 ಡೇಟಾವಿಜ್ ಪ್ರೋ - ಸುಧಾರಿತ ವಿಶ್ಲೇಷಣೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "upload": "📁 ನಿಮ್ಮ ಡೇಟಾವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "file_upload": "CSV ಫೈಲ್ ಆಯ್ಕೆಮಾಡಿ",
        "overview": "📊 ಅವಲೋಕನ",
        "visualizations": "📈 ದೃಶ್ಯೀಕರಣಗಳು",
        "data_explorer": "🔍 ಡೇಟಾ ಎಕ್ಸ್‌ಪ್ಲೋರರ್",
        "ai_assistant": "🤖 AI ಸಹಾಯಕ",
        "summary": "📋 ಸಾರಾಂಶ",
        "chat_placeholder": "ನಿಮ್ಮ ಡೇಟಾ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ...",
        "ask_ai": "🚀 AI ಸಹಾಯಕನನ್ನು ಕೇಳಿ"
    },
    "മലയാളം": {
        "title": "🚀 ഡാറ്റാവിസ് പ്രോ - അഡ്വാൻസ്ഡ് അനാലിറ്റിക്സ് ഡാഷ്ബോർഡ്",
        "upload": "📁 നിങ്ങളുടെ ഡാറ്റ അപ്‌ലോഡ് ചെയ്യുക",
        "file_upload": "CSV ഫയൽ തിരഞ്ഞെടുക്കുക",
        "overview": "📊 അവലോകനം",
        "visualizations": "📈 വിഷുവലൈസേഷൻസ്",
        "data_explorer": "🔍 ഡാറ്റ എക്സ്പ്ലോറർ",
        "ai_assistant": "🤖 AI അസിസ്റ്റന്റ്",
        "summary": "📋 സംഗ്രഹം",
        "chat_placeholder": "നിങ്ങളുടെ ഡാറ്റയെക്കുറിച്ച് ചോദിക്കുക...",
        "ask_ai": "🚀 AI അസിസ്റ്റന്റിനോട് ചോദിക്കുക"
    },
    "ਪੰਜਾਬੀ": {
        "title": "🚀 ਡੇਟਾਵਿਜ਼ ਪ੍ਰੋ - ਉੱਨਤ ਵਿਸ਼ਲੇਸ਼ਣ ਡੈਸ਼ਬੋਰਡ",
        "upload": "📁 ਆਪਣਾ ਡੇਟਾ ਅਪਲੋਡ ਕਰੋ",
        "file_upload": "CSV ਫਾਈਲ ਚੁਣੋ",
        "overview": "📊 ਸੰਖੇਪ",
        "visualizations": "📈 ਵਿਜ਼ੂਅਲਾਈਜ਼ੇਸ਼ਨ",
        "data_explorer": "🔍 ਡੇਟਾ ਐਕਸਪਲੋਰਰ",
        "ai_assistant": "🤖 AI ਸਹਾਇਕ",
        "summary": "📋 ਸਾਰ",
        "chat_placeholder": "ਆਪਣੇ ਡੇਟਾ ਬਾਰੇ ਸਵਾਲ ਪੁੱਛੋ...",
        "ask_ai": "🚀 AI ਸਹਾਇਕ ਤੋਂ ਪੁੱਛੋ"
    },
    "ଓଡ଼ିଆ": {
        "title": "🚀 ଡାଟାଭିଜ୍ ପ୍ରୋ - ଉନ୍ନତ ବିଶ୍ଳେଷଣ ଡ୍ୟାସବୋର୍ଡ",
        "upload": "📁 ଆପଣଙ୍କ ଡାଟା ଅପଲୋଡ୍ କରନ୍ତୁ",
        "file_upload": "CSV ଫାଇଲ୍ ବାଛନ୍ତୁ",
        "overview": "📊 ସାରାଂଶ",
        "visualizations": "📈 ଭିଜୁଆଲାଇଜେସନ୍",
        "data_explorer": "🔍 ଡାଟା ଏକ୍ସପ୍ଲୋରର୍",
        "ai_assistant": "🤖 AI ସହାୟକ",
        "summary": "📋 ସଂଖିପ୍ତ ବିବରଣୀ",
        "chat_placeholder": "ଆପଣଙ୍କ ଡାଟା ବିଷୟରେ ପ୍ରଶ୍ନ କରନ୍ତୁ...",
        "ask_ai": "🚀 AI ସହାୟକଙ୍କୁ ପଚାରନ୍ତୁ"
    },
    "অসমীয়া": {
        "title": "🚀 ডেটাভিজ প্ৰ' - উন্নত বিশ্লেষণ ডেছব'ৰ্ড",
        "upload": "📁 আপোনাৰ ডেটা আপল'ড কৰক",
        "file_upload": "CSV ফাইল বাছনি কৰক",
        "overview": "📊 চমু আভাস",
        "visualizations": "📈 ভিজুৱেলাইজেচন",
        "data_explorer": "🔍 ডেটা এক্সপ্ল'ৰাৰ",
        "ai_assistant": "🤖 AI সহায়ক",
        "summary": "📋 সাৰাংশ",
        "chat_placeholder": "আপোনাৰ ডেটাৰ বিষয়ে প্ৰশ্ন কৰক...",
        "ask_ai": "🚀 AI সহায়কক সুধক"
    },
    "اردو": {
        "title": "🚀 ڈیٹا وز پرو - ایڈوانسڈ ایناَلِٹکس ڈیش بورڈ",
        "upload": "📁 اپنا ڈیٹا اپ لوڈ کریں",
        "file_upload": "CSV فائل منتخب کریں",
        "overview": "📊 جائزہ",
        "visualizations": "📈 تصویری نمائندگی",
        "data_explorer": "🔍 ڈیٹا ایکسپلورر",
        "ai_assistant": "🤖 AI اسسٹنٹ",
        "summary": "📋 خلاصہ",
        "chat_placeholder": "اپنے ڈیٹا کے بارے میں سوال پوچھیں...",
        "ask_ai": "🚀 AI اسسٹنٹ سے پوچھیں"
    }
}

# Theme configurations
THEMES = {
    "Modern Blue": {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "bg_color": "#ffffff",
        "text_color": "#000000",
        "chat_user_bg": "#e3f2fd",
        "chat_bot_bg": "#f3e5f5",
        "gradient": "linear-gradient(90deg, #667eea 0%, #764ba2 100%)"
    },
    "Dark Mode": {
        "primary": "#00d4aa",
        "secondary": "#ff6b6b", 
        "bg_color": "#1e1e1e",
        "text_color": "#ffffff",
        "chat_user_bg": "#2d3748",
        "chat_bot_bg": "#4a5568",
        "gradient": "linear-gradient(90deg, #00d4aa 0%, #ff6b6b 100%)"
    },
    "Indian Orange": {
        "primary": "#ff9933",
        "secondary": "#138808",
        "bg_color": "#ffffff", 
        "text_color": "#000000",
        "chat_user_bg": "#fff3cd",
        "chat_bot_bg": "#d4edda",
        "gradient": "linear-gradient(90deg, #ff9933 0%, #138808 100%)"
    },
    "Royal Purple": {
        "primary": "#8e44ad",
        "secondary": "#e74c3c",
        "bg_color": "#f8f9fa",
        "text_color": "#2c3e50",
        "chat_user_bg": "#e8d5f2",
        "chat_bot_bg": "#fadbd8",
        "gradient": "linear-gradient(90deg, #8e44ad 0%, #e74c3c 100%)"
    }
}

def get_text(key):
    """Get translated text based on selected language"""
    return LANGUAGES[st.session_state.language].get(key, key)

def get_theme():
    """Get current theme configuration"""
    return THEMES[st.session_state.theme]

# Custom CSS for better UI/UX with dynamic theming
def get_custom_css():
    theme = get_theme()
    return f"""
<style>
    .main-header {{
        font-size: 3rem;
        font-weight: bold;
        color: {theme['primary']};
        text-align: center;
        margin-bottom: 2rem;
        background: {theme['gradient']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .metric-card {{
        background: {theme['gradient']};
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }}
    
    .sidebar-content {{
        background-color: {theme['bg_color']};
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }}
    
    .chat-message {{
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: {theme['text_color']} !important;
    }}
    
    .user-message {{
        background-color: {theme['chat_user_bg']};
        border-left: 4px solid {theme['primary']};
        color: {theme['text_color']} !important;
    }}
    
    .bot-message {{
        background-color: {theme['chat_bot_bg']};
        border-left: 4px solid {theme['secondary']};
        color: {theme['text_color']} !important;
    }}
    
    .stButton > button {{
        background: {theme['gradient']};
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
    }}
    
    .stSelectbox > div > div {{
        background-color: {theme['bg_color']};
        color: {theme['text_color']};
    }}
    
    .main .block-container {{
        background-color: {theme['bg_color']};
        color: {theme['text_color']};
    }}
</style>
"""

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.is_large_dataset = len(df) > 50000 or df.memory_usage(deep=True).sum() / 1024**2 > 100
        self.sample_size = min(len(df), st.session_state.file_processing_config['max_sample_size'])
        
    def get_optimized_sample(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """Get optimized sample for analysis and visualization"""
        if sample_size is None:
            sample_size = self.sample_size
            
        if len(self.df) <= sample_size:
            return self.df
        
        # Stratified sampling for better representation
        if self.df.select_dtypes(include=['object']).shape[1] > 0:
            # Sample maintaining categorical distribution
            categorical_cols = self.df.select_dtypes(include=['object']).columns[:2]  # Use first 2 categorical columns
            try:
                sample = self.df.groupby(categorical_cols[0], group_keys=False).apply(
                    lambda x: x.sample(min(len(x), max(1, sample_size // self.df[categorical_cols[0]].nunique())))
                ).reset_index(drop=True)
                return sample.head(sample_size)
            except:
                pass
        
        # Random sampling as fallback
        return self.df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_basic_info(_self):
        """Get basic information about the dataset with performance optimizations"""
        df = _self.df
        memory_usage_mb = df.memory_usage(deep=True).sum() / 1024**2
        
        # Fast approximation for very large datasets
        if len(df) > 100000:
            sample_df = _self.get_optimized_sample(10000)
            missing_sample = sample_df.isnull().sum().sum()
            missing_estimate = int((missing_sample / len(sample_df)) * len(df))
        else:
            missing_estimate = df.isnull().sum().sum()
        
        info = {
            'rows': len(df),
            'columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns),
            'missing_values': missing_estimate,
            'memory_usage': f"{memory_usage_mb:.2f} MB",
            'is_large_dataset': _self.is_large_dataset,
            'data_quality_score': max(0, 100 - (missing_estimate / (len(df) * len(df.columns)) * 100))
        }
        return info
    
    @st.cache_data(ttl=3600)
    def get_column_analysis(_self):
        """Analyze each column in detail with optimizations for large datasets"""
        df = _self.df
        
        # Use sample for large datasets
        if _self.is_large_dataset:
            analysis_df = _self.get_optimized_sample(50000)
            st.info(f"📊 Analysis based on {len(analysis_df):,} sample rows (from {len(df):,} total)")
        else:
            analysis_df = df
            
        analysis = {}
        
        # Process columns in batches for better performance
        for col in analysis_df.columns:
            try:
                col_info = {
                    'dtype': str(analysis_df[col].dtype),
                    'null_count': analysis_df[col].isnull().sum(),
                    'null_percentage': (analysis_df[col].isnull().sum() / len(analysis_df)) * 100,
                    'unique_count': analysis_df[col].nunique(),
                    'memory_usage_mb': analysis_df[col].memory_usage(deep=True) / 1024**2
                }
                
                # Add type-specific analysis
                if analysis_df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    col_info.update({
                        'mean': float(analysis_df[col].mean()) if not analysis_df[col].isnull().all() else 0,
                        'median': float(analysis_df[col].median()) if not analysis_df[col].isnull().all() else 0,
                        'std': float(analysis_df[col].std()) if not analysis_df[col].isnull().all() else 0,
                        'min': float(analysis_df[col].min()) if not analysis_df[col].isnull().all() else 0,
                        'max': float(analysis_df[col].max()) if not analysis_df[col].isnull().all() else 0,
                        'outliers': _self._detect_outliers(analysis_df[col])
                    })
                elif analysis_df[col].dtype == 'object':
                    col_info.update({
                        'top_values': analysis_df[col].value_counts().head(5).to_dict(),
                        'avg_length': analysis_df[col].astype(str).str.len().mean() if not analysis_df[col].isnull().all() else 0
                    })
                    
                analysis[col] = col_info
                
            except Exception as e:
                # Fallback for problematic columns
                analysis[col] = {
                    'dtype': str(analysis_df[col].dtype),
                    'null_count': analysis_df[col].isnull().sum(),
                    'null_percentage': (analysis_df[col].isnull().sum() / len(analysis_df)) * 100,
                    'unique_count': 0,
                    'error': str(e)
                }
                
        return analysis
    
    def _detect_outliers(self, series: pd.Series) -> Dict[str, int]:
        """Detect outliers using IQR method"""
        try:
            if series.dtype not in ['int64', 'float64', 'int32', 'float32']:
                return {'count': 0, 'percentage': 0}
                
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((series < lower_bound) | (series > upper_bound)).sum()
            return {
                'count': int(outliers),
                'percentage': float((outliers / len(series)) * 100)
            }
        except:
            return {'count': 0, 'percentage': 0}
    
    def get_data_profiling_report(self) -> Dict[str, Any]:
        """Generate comprehensive data profiling report"""
        basic_info = self.get_basic_info()
        column_analysis = self.get_column_analysis()
        
        # Advanced insights
        insights = {
            'data_completeness': 100 - (basic_info['missing_values'] / (basic_info['rows'] * basic_info['columns']) * 100),
            'schema_complexity': 'High' if basic_info['columns'] > 50 else 'Medium' if basic_info['columns'] > 20 else 'Low',
            'size_category': 'Large' if basic_info['rows'] > 100000 else 'Medium' if basic_info['rows'] > 10000 else 'Small',
            'recommendations': self._generate_recommendations(basic_info, column_analysis)
        }
        
        return {
            'basic_info': basic_info,
            'column_analysis': column_analysis,
            'insights': insights
        }
    
    def _generate_recommendations(self, basic_info: Dict, column_analysis: Dict) -> list:
        """Generate data quality and analysis recommendations"""
        recommendations = []
        
        # Missing data recommendations
        if basic_info['missing_values'] > basic_info['rows'] * 0.1:
            recommendations.append("🚨 High missing data detected. Consider data imputation or removal of incomplete records.")
        
        # Memory optimization
        if basic_info['is_large_dataset']:
            recommendations.append("💾 Large dataset detected. Using optimized sampling for analysis and visualizations.")
        
        # Data type optimization
        memory_heavy_cols = [col for col, info in column_analysis.items() 
                           if info.get('memory_usage_mb', 0) > 10]
        if memory_heavy_cols:
            recommendations.append(f"🔍 Consider optimizing data types for columns: {', '.join(memory_heavy_cols[:3])}")
        
        # Outlier detection
        outlier_cols = [col for col, info in column_analysis.items() 
                       if info.get('outliers', {}).get('percentage', 0) > 5]
        if outlier_cols:
            recommendations.append(f"📈 Outliers detected in: {', '.join(outlier_cols[:3])}. Consider investigation or treatment.")
        
        return recommendations

class ChatBot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.max_context_length = 8000  # Increased context for complex data
        self.response_cache = {}  # Simple response caching
    
    def generate_comprehensive_data_context(self, df: pd.DataFrame, analyzer: DataAnalyzer) -> str:
        """Generate comprehensive context about the dataset for complex analysis"""
        basic_info = analyzer.get_basic_info()
        
        # Use sample for large datasets to generate context
        if analyzer.is_large_dataset:
            context_df = analyzer.get_optimized_sample(5000)
            size_note = f"(Analysis based on {len(context_df):,} sample rows from {len(df):,} total)"
        else:
            context_df = df
            size_note = ""
        
        # Generate statistical summary
        numeric_summary = ""
        categorical_summary = ""
        
        try:
            # Numeric columns analysis
            numeric_cols = context_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                numeric_stats = context_df[numeric_cols].describe()
                numeric_summary = f"\nNumeric Columns Summary:\n{numeric_stats.to_string()}\n"
            
            # Categorical columns analysis
            categorical_cols = context_df.select_dtypes(include=['object']).columns[:5]  # Limit to 5 categorical columns
            if len(categorical_cols) > 0:
                cat_info = []
                for col in categorical_cols:
                    try:
                        top_values = context_df[col].value_counts().head(3)
                        cat_info.append(f"{col}: Top values - {dict(top_values)}")
                    except:
                        cat_info.append(f"{col}: Analysis unavailable")
                categorical_summary = f"\nCategorical Columns Summary:\n" + "\n".join(cat_info) + "\n"
        
        except Exception as e:
            st.warning(f"Some statistical analysis skipped due to data complexity: {str(e)}")
        
        # Data quality insights
        quality_insights = self._analyze_data_quality(context_df, basic_info)
        
        # Generate correlation insights for numeric data
        correlation_insights = ""
        try:
            if len(numeric_cols) > 1:
                corr_matrix = context_df[numeric_cols].corr()
                high_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7 and not np.isnan(corr_val):
                            high_corr.append(f"{corr_matrix.columns[i]} ↔ {corr_matrix.columns[j]}: {corr_val:.2f}")
                
                if high_corr:
                    correlation_insights = f"\nHigh Correlations Found:\n" + "\n".join(high_corr[:5]) + "\n"
        except Exception:
            pass
        
        # Sample data for context (limited to prevent token overflow)
        sample_data = ""
        try:
            if len(context_df) > 0:
                sample_rows = min(3, len(context_df))
                sample_data = f"\nSample Data ({sample_rows} rows):\n{context_df.head(sample_rows).to_string()}\n"
        except Exception:
            sample_data = "\nSample data unavailable due to complexity.\n"
        
        context = f"""
DATASET ANALYSIS CONTEXT {size_note}:

=== BASIC INFORMATION ===
- Total Records: {basic_info['rows']:,}
- Total Features: {basic_info['columns']}
- Numeric Columns: {basic_info['numeric_columns']}
- Categorical Columns: {basic_info['categorical_columns']}
- DateTime Columns: {basic_info['datetime_columns']}
- Missing Values: {basic_info['missing_values']:,}
- Memory Usage: {basic_info['memory_usage']}
- Data Quality Score: {basic_info['data_quality_score']:.1f}%
- Dataset Size: {basic_info.get('size_category', 'Unknown')}

=== COLUMN INFORMATION ===
Columns: {', '.join(context_df.columns.tolist())}
Data Types: {dict(context_df.dtypes.astype(str))}
{numeric_summary}{categorical_summary}{correlation_insights}
=== DATA QUALITY INSIGHTS ===
{quality_insights}
{sample_data}
=== ANALYSIS GUIDELINES ===
You are an expert data scientist analyzing this dataset. Provide accurate, 
insightful responses based ONLY on this data. Focus on:
1. Data patterns and trends
2. Statistical insights
3. Data quality issues
4. Actionable recommendations
5. Domain-specific insights when applicable

For large datasets, note that analysis is based on representative samples.
"""
        
        # Truncate context if too long
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "\n[Context truncated for optimal processing]"
        
        return context
    
    def _analyze_data_quality(self, df: pd.DataFrame, basic_info: Dict) -> str:
        """Analyze data quality and return insights"""
        insights = []
        
        # Missing data analysis
        missing_pct = (basic_info['missing_values'] / (basic_info['rows'] * basic_info['columns'])) * 100
        if missing_pct > 10:
            insights.append(f"⚠️ High missing data: {missing_pct:.1f}% of total values")
        elif missing_pct > 5:
            insights.append(f"⚠️ Moderate missing data: {missing_pct:.1f}% of total values")
        else:
            insights.append(f"✅ Low missing data: {missing_pct:.1f}% of total values")
        
        # Duplicate analysis
        try:
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                insights.append(f"🔄 {duplicates:,} duplicate rows found ({(duplicates/len(df)*100):.1f}%)")
            else:
                insights.append("✅ No duplicate rows detected")
        except:
            insights.append("ℹ️ Duplicate analysis unavailable")
        
        # Data consistency
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                inf_values = np.isinf(df[numeric_cols].select_dtypes(include=[np.number])).sum().sum()
                if inf_values > 0:
                    insights.append(f"⚠️ {inf_values} infinite values detected")
                else:
                    insights.append("✅ No infinite values detected")
        except:
            pass
        
        return "\n".join(insights)
    
    def get_response(self, question: str, data_context: str, analyzer: DataAnalyzer = None) -> str:
        """Get enhanced response from Gemini API with complex data handling"""
        try:
            # Check cache first
            cache_key = f"{question[:50]}_{len(data_context)}"
            if cache_key in self.response_cache:
                return self.response_cache[cache_key]
            
            # Get response length preference
            response_length = st.session_state.get('response_length', 'Concise')
            selected_language = st.session_state.get('language', 'English')
            
            # Enhanced response length instructions
            length_instructions = {
                "Short": "Provide a brief, 1-2 sentence answer with key insights only.",
                "Concise": "Provide a clear, focused answer in 2-3 paragraphs with specific data insights.",
                "Detailed": "Provide a comprehensive analysis with detailed explanations, statistics, and actionable recommendations.",
                "Technical": "Provide deep technical analysis with statistical details, methodology, data quality assessment, and advanced insights."
            }
            
            # Language instruction
            language_instruction = f"Respond in {selected_language}. " if selected_language != "English" else ""
            
            # Enhanced prompt for complex data analysis
            enhanced_prompt = f"""
{language_instruction}You are an expert data scientist analyzing complex datasets. 

{length_instructions[response_length]}

IMPORTANT GUIDELINES:
1. Base your analysis ONLY on the provided dataset context
2. Provide specific numbers, percentages, and statistical insights when relevant
3. Identify patterns, trends, and anomalies in the data
4. Suggest actionable insights and recommendations
5. Highlight data quality issues if present
6. For large datasets, acknowledge that analysis is based on representative samples
7. Be precise and avoid generic responses

DATASET CONTEXT:
{data_context}

USER QUESTION: {question}

ANALYSIS:
"""
            
            # Generate response with error handling
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more factual responses
                    max_output_tokens=2048 if response_length == "Technical" else 1024,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response and response.text:
                result = response.text.strip()
                
                # Cache the response
                self.response_cache[cache_key] = result
                
                # Clean cache if it gets too large
                if len(self.response_cache) > 50:
                    # Remove oldest entries
                    oldest_keys = list(self.response_cache.keys())[:10]
                    for key in oldest_keys:
                        del self.response_cache[key]
                
                return result
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                return "🚕 API quota exceeded. Please try again later or use a simpler question."
            elif "safety" in error_msg:
                return "🛡️ Response blocked by safety filters. Please rephrase your question."
            else:
                return f"⚠️ Error in AI analysis: {str(e)}. Please try a different question."
    
    def generate_data_insights(self, df: pd.DataFrame, analyzer: DataAnalyzer) -> str:
        """Generate automatic insights for complex datasets"""
        try:
            basic_info = analyzer.get_basic_info()
            
            # Get comprehensive context for insights
            context = self.generate_comprehensive_data_context(df, analyzer)
            
            insights_prompt = f"""
You are an expert data scientist. Analyze this dataset and provide 5 key automatic insights.

{context}

Provide insights in the following format:
🔍 **DATA INSIGHTS:**

**1. Dataset Overview:**
[Provide overview of the dataset size, structure, and complexity]

**2. Data Quality Assessment:**
[Analyze data completeness, missing values, and quality issues]

**3. Key Patterns & Trends:**
[Identify significant patterns, correlations, or trends in the data]

**4. Notable Findings:**
[Highlight interesting discoveries, outliers, or anomalies]

**5. Actionable Recommendations:**
[Suggest next steps, data cleaning actions, or analysis directions]

Focus on actionable insights that help users understand their data better.
Use specific numbers and percentages from the dataset.
"""
            
            response = self.model.generate_content(
                insights_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=1500,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            return response.text if response and response.text else "📊 Automatic insights generation completed, but response was empty. Try asking specific questions about your data."
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                return "🚕 **API Quota Information:** The AI service has reached its usage limit. Please try again later or ask specific questions about your data using the chat interface below."
            elif "safety" in error_msg:
                return "🛡️ **Content Filter:** The automatic insight generation was filtered for safety. Your data appears to contain content that triggered safety protocols. Try asking specific analytical questions instead."
            else:
                return f"⚠️ **Insight Generation Note:** Automatic insights are temporarily unavailable ({str(e)[:100]}). However, you can still ask specific questions about your data using the AI chat below, which works independently."
    
    def enhance_user_understanding(self, question: str) -> str:
        """Enhance user questions for better AI understanding"""
        # Common data analysis patterns and their enhanced versions
        enhancement_patterns = {
            # Statistical questions
            "mean": "statistical mean average",
            "average": "statistical mean average",
            "correlation": "statistical correlation relationship",
            "trend": "trend pattern over time",
            "outlier": "outlier anomaly unusual values",
            
            # Data quality questions  
            "missing": "missing null empty values",
            "null": "missing null empty values",
            "quality": "data quality completeness accuracy",
            "clean": "data cleaning preprocessing",
            
            # Pattern questions
            "pattern": "pattern trend relationship",
            "relationship": "relationship correlation dependency",
            "distribution": "distribution spread frequency",
            "summary": "statistical summary overview analysis",
            
            # Business questions
            "insight": "business insight actionable finding",
            "recommend": "recommendation suggestion action",
            "predict": "prediction forecast future trend",
            "compare": "comparison analysis difference"
        }
        
        enhanced_question = question.lower()
        for pattern, enhancement in enhancement_patterns.items():
            if pattern in enhanced_question:
                enhanced_question = enhanced_question.replace(pattern, enhancement)
        
        return enhanced_question
    
    def get_response(self, question: str, data_context: str, analyzer: DataAnalyzer = None) -> str:
        """Get enhanced response from Gemini API with complex data handling and improved user understanding"""
        try:
            # Check cache first
            cache_key = f"{question[:50]}_{len(data_context)}"
            if cache_key in self.response_cache:
                return self.response_cache[cache_key]
            
            # Get response length preference
            response_length = st.session_state.get('response_length', 'Concise')
            selected_language = st.session_state.get('language', 'English')
            
            # Enhanced response length instructions
            length_instructions = {
                "Short": "Provide a brief, 1-2 sentence answer with key insights only.",
                "Concise": "Provide a clear, focused answer in 2-3 paragraphs with specific data insights.",
                "Detailed": "Provide a comprehensive analysis with detailed explanations, statistics, and actionable recommendations.",
                "Technical": "Provide deep technical analysis with statistical details, methodology, data quality assessment, and advanced insights."
            }
            
            # Language instruction with cultural context
            language_instructions = {
                "English": "Respond in clear, professional English.",
                "हिंदी": "हिंदी में स्पष्ट और व्यावसायिक भाषा में उत्तर दें।",
                "తెలుగు": "తెలుగులో స్పష్టంగా మరియు వృత్తిపరంగా సమాధానం ఇవ్వండి।",
                "தமிழ்": "தமிழில் தெளிவாகவும் தொழில்முறையாகவும் பதிலளிக்கவும்।",
                "বাংলা": "বাংলায় স্পষ্ট এবং পেশাদার ভাষায় উত্তর দিন।",
                "ગુજરાતી": "ગુજરાતીમાં સ્પષ્ટ અને વ્યાવસાયિક ભાષામાં જવાબ આપો।",
                "मराठी": "मराठीत स्पष्ट आणि व्यावसायिक भाषेत उत्तर द्या।",
                "ಕನ್ನಡ": "ಕನ್ನಡದಲ್ಲಿ ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ವೃತ್ತಿಪರವಾಗಿ ಉತ್ತರಿಸಿ।",
                "മലയാളം": "മലയാളത്തിൽ വ്യക്തമായും പ്രൊഫഷണലായും ഉത്തരം നൽകുക।",
                "ਪੰਜਾਬੀ": "ਪੰਜਾਬੀ ਵਿੱਚ ਸਪੱਸ਼ਟ ਅਤੇ ਪੇਸ਼ੇਵਰ ਭਾਸ਼ਾ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।",
                "ଓଡ଼ିଆ": "ଓଡ଼ିଆରେ ସ୍ପଷ୍ଟ ଏବଂ ବୃତ୍ତିଗତ ଭାଷାରେ ଉତ୍ତର ଦିଅନ୍ତୁ।",
                "অসমীয়া": "অসমীয়াত স্পষ্ট আৰু বৃত্তিগত ভাষাত উত্তৰ দিয়ক।",
                "اردو": "اردو میں واضح اور پیشہ ورانہ زبان میں جواب دیں۔"
            }
            
            language_instruction = language_instructions.get(selected_language, "Respond in clear, professional English.")
            
            # Enhance user question for better understanding
            enhanced_question = self.enhance_user_understanding(question)
            
            # Enhanced prompt for complex data analysis with better user understanding
            enhanced_prompt = f"""
{language_instruction}

You are an expert data scientist with advanced analytical capabilities. {length_instructions[response_length]}

CRITICAL GUIDELINES FOR USER UNDERSTANDING:
1. ALWAYS base your analysis ONLY on the provided dataset context
2. Understand the user's intent even if questions are simple or complex
3. Provide specific numbers, percentages, and statistical insights when relevant
4. Identify patterns, trends, and anomalies in the data
5. Suggest actionable insights and recommendations
6. Highlight data quality issues if present
7. For large datasets, acknowledge that analysis is based on representative samples
8. Be precise and avoid generic responses
9. If the question is unclear, provide the best interpretation and mention alternatives
10. Always relate your response to the actual data provided

USER QUESTION ANALYSIS:
Original Question: "{question}"
Enhanced Understanding: "{enhanced_question}"

DATASET CONTEXT:
{data_context}

DETAILED ANALYSIS RESPONSE:
"""
            
            # Generate response with error handling
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more factual responses
                    max_output_tokens=2048 if response_length == "Technical" else 1024,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response and response.text:
                result = response.text.strip()
                
                # Add context note for large datasets
                if analyzer and analyzer.is_large_dataset:
                    result += "\n\n📊 *Note: Analysis based on representative sample from large dataset for optimal performance.*"
                
                # Cache the response
                self.response_cache[cache_key] = result
                
                # Clean cache if it gets too large
                if len(self.response_cache) > 50:
                    # Remove oldest entries
                    oldest_keys = list(self.response_cache.keys())[:10]
                    for key in oldest_keys:
                        del self.response_cache[key]
                
                return result
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question or ask about specific aspects of your data."
                
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                return "🚕 **API Usage Notice:** The AI service has reached its usage limit. Please try again in a few minutes. You can still explore your data using the visualizations above."
            elif "safety" in error_msg:
                return "🛡️ **Content Notice:** Your question was filtered by safety protocols. Please try rephrasing your question or ask about different aspects of your data."
            elif "context" in error_msg or "token" in error_msg:
                return "📊 **Large Data Notice:** Your dataset is very complex. Try asking simpler questions or use the 'Short' response mode for better performance."
            else:
                return f"⚠️ **Processing Notice:** There was a temporary issue processing your question. Please try: 1) Simplifying your question, 2) Using different response length, or 3) Asking about specific columns or data aspects. Error details: {str(e)[:100]}..."
    
    # Maintain backward compatibility
    def generate_data_context(self, df: pd.DataFrame) -> str:
        """Backward compatibility method"""
        analyzer = DataAnalyzer(df)
        return self.generate_comprehensive_data_context(df, analyzer)

@st.cache_data(ttl=3600)  # Cache visualizations for 1 hour
def create_visualizations(df):
    """Create various visualizations based on data types with optimizations for large datasets"""
    # Use sample for large datasets to improve performance
    display_df = df
    if len(df) > 50000:
        display_df = df.sample(n=50000, random_state=42)
        st.info(f"📊 Visualizations based on {len(display_df):,} sample rows (from {len(df):,} total)")
    
    numeric_cols = display_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = display_df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = display_df.select_dtypes(include=['datetime64']).columns.tolist()
    
    visualizations = []
    
    try:
        # Correlation heatmap for numeric columns
        if len(numeric_cols) > 1:
            # Limit correlations to avoid clutter
            corr_cols = numeric_cols[:15]  # Max 15 columns for readability
            corr_matrix = display_df[corr_cols].corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title=f"📊 Correlation Matrix ({len(corr_cols)} columns)",
                color_continuous_scale="RdBu",
                zmin=-1, zmax=1
            )
            fig_corr.update_layout(height=600, font_size=10)
            visualizations.append(("Correlation Matrix", fig_corr))
        
        # Enhanced distribution plots for numeric columns
        for i, col in enumerate(numeric_cols[:6]):  # Limit to 6 columns
            try:
                # Remove outliers for better visualization
                Q1 = display_df[col].quantile(0.25)
                Q3 = display_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Filter data for visualization
                filtered_data = display_df[(display_df[col] >= lower_bound) & (display_df[col] <= upper_bound)]
                
                # Create distribution with statistics
                fig_hist = px.histogram(
                    filtered_data, 
                    x=col, 
                    title=f"📈 Distribution of {col} (Outliers Removed)",
                    nbins=min(50, len(filtered_data) // 100),
                    color_discrete_sequence=['#667eea'],
                    marginal="box"
                )
                
                # Add statistics
                mean_val = display_df[col].mean()
                median_val = display_df[col].median()
                fig_hist.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                                 annotation_text=f"Mean: {mean_val:.2f}")
                fig_hist.add_vline(x=median_val, line_dash="dash", line_color="green", 
                                 annotation_text=f"Median: {median_val:.2f}")
                
                fig_hist.update_layout(height=450)
                visualizations.append((f"Distribution - {col}", fig_hist))
            except Exception as e:
                st.warning(f"Skipped distribution for {col}: {str(e)}")
        
        # Enhanced box plots for numeric columns
        if len(numeric_cols) >= 2:
            try:
                fig_box = go.Figure()
                box_cols = numeric_cols[:8]  # Limit to 8 for readability
                
                for col in box_cols:
                    fig_box.add_trace(go.Box(
                        y=display_df[col], 
                        name=col,
                        boxpoints='outliers',
                        jitter=0.3,
                        whiskerwidth=0.2
                    ))
                
                fig_box.update_layout(
                    title=f"📦 Box Plots - Numeric Columns ({len(box_cols)} columns)",
                    height=500,
                    showlegend=False
                )
                visualizations.append(("Box Plots", fig_box))
            except Exception as e:
                st.warning(f"Box plot creation failed: {str(e)}")
        
        # Enhanced bar charts for categorical columns
        for i, col in enumerate(categorical_cols[:4]):  # Limit to 4 categorical columns
            try:
                value_counts = display_df[col].value_counts().head(15)  # Top 15 values
                
                fig_bar = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f"📊 Top 15 Values in {col}",
                    color=value_counts.values,
                    color_continuous_scale="viridis",
                    text=value_counts.values
                )
                
                fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
                fig_bar.update_layout(height=500, showlegend=False)
                visualizations.append((f"Bar Chart - {col}", fig_bar))
            except Exception as e:
                st.warning(f"Bar chart creation failed for {col}: {str(e)}")
        
        # Enhanced scatter plots with trend lines
        if len(numeric_cols) >= 2:
            # Create smart combinations (highest correlations first)
            try:
                corr_matrix = display_df[numeric_cols].corr()
                scatter_pairs = []
                
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        corr_val = abs(corr_matrix.iloc[i, j])
                        if not np.isnan(corr_val):
                            scatter_pairs.append((numeric_cols[i], numeric_cols[j], corr_val))
                
                # Sort by correlation strength
                scatter_pairs.sort(key=lambda x: x[2], reverse=True)
                
                # Create top 3 scatter plots
                for col1, col2, corr_val in scatter_pairs[:3]:
                    try:
                        fig_scatter = px.scatter(
                            display_df,
                            x=col1,
                            y=col2,
                            title=f"🎯 {col1} vs {col2} (Correlation: {corr_val:.3f})",
                            color_discrete_sequence=['#764ba2'],
                            trendline="ols",
                            opacity=0.6
                        )
                        fig_scatter.update_layout(height=500)
                        visualizations.append((f"Scatter - {col1} vs {col2}", fig_scatter))
                    except:
                        continue
            except Exception as e:
                st.warning(f"Scatter plot creation failed: {str(e)}")
        
        # Time series plots for datetime columns
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            try:
                date_col = datetime_cols[0]
                numeric_col = numeric_cols[0]
                
                # Convert to datetime if needed
                if display_df[date_col].dtype != 'datetime64[ns]':
                    display_df[date_col] = pd.to_datetime(display_df[date_col], errors='coerce')
                
                # Remove rows with invalid dates
                time_data = display_df.dropna(subset=[date_col, numeric_col])
                
                if len(time_data) > 0:
                    fig_time = px.line(
                        time_data.sort_values(date_col),
                        x=date_col,
                        y=numeric_col,
                        title=f"🕰️ Time Series: {numeric_col} over {date_col}",
                        color_discrete_sequence=['#667eea']
                    )
                    fig_time.update_layout(height=450)
                    visualizations.append((f"Time Series - {numeric_col}", fig_time))
            except Exception as e:
                st.warning(f"Time series plot failed: {str(e)}")
        
        # Data quality visualization
        try:
            missing_data = display_df.isnull().sum()
            if missing_data.sum() > 0:
                missing_data = missing_data[missing_data > 0].sort_values(ascending=True)
                
                fig_missing = px.bar(
                    x=missing_data.values,
                    y=missing_data.index,
                    orientation='h',
                    title=f"⚠️ Missing Data by Column",
                    color=missing_data.values,
                    color_continuous_scale="Reds"
                )
                fig_missing.update_layout(height=400)
                visualizations.append(("Missing Data Analysis", fig_missing))
        except Exception as e:
            st.warning(f"Missing data visualization failed: {str(e)}")
    
    except Exception as e:
        st.error(f"Visualization creation failed: {str(e)}")
        st.info("💡 This might be due to data complexity. Try with a smaller sample or simpler data.")
    
    return visualizations

def main():
    # Apply dynamic CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Header with language, theme, and response controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown(f'<h1 class="main-header">{get_text("title")}</h1>', unsafe_allow_html=True)
    
    with col2:
        new_language = st.selectbox(
            "🌍 Language",
            list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_selector"
        )
        if new_language != st.session_state.language:
            st.session_state.language = new_language
            st.rerun()
    
    with col3:
        new_theme = st.selectbox(
            "🎨 Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme),
            key="theme_selector"
        )
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
    
    with col4:
        st.session_state.response_length = st.selectbox(
            "💬 Response",
            ["Short", "Concise", "Detailed", "Technical"],
            index=["Short", "Concise", "Detailed", "Technical"].index(st.session_state.response_length),
            key="response_selector"
        )
    
    # Sidebar with persistent file handling
    with st.sidebar:
        st.markdown(f"### {get_text('upload')}")
        
        # Show current file status
        if st.session_state.uploaded_data is not None:
            st.success(f"✅ File loaded: {st.session_state.file_name}")
            st.info(f"Rows: {len(st.session_state.uploaded_data):,} | Columns: {len(st.session_state.uploaded_data.columns)}")
            
            # Option to upload new file
            if st.button("🔄 Upload New File"):
                st.session_state.uploaded_data = None
                st.session_state.file_name = None
                st.rerun()
        
        # File uploader (only show if no file is loaded)
        if st.session_state.uploaded_data is None:
            uploaded_file = st.file_uploader(
                get_text("file_upload"),
                type=["csv", "xlsx", "xls"],
                help="Upload CSV, Excel files. Large files (>100MB) supported with optimizations!"
            )
        else:
            uploaded_file = None
        
        if uploaded_file is not None:
            # Enhanced file processing with progress indication
            with st.spinner("🔄 Processing file... Please wait for large files."):
                try:
                    file_size_mb = uploaded_file.size / (1024 * 1024)
                    st.info(f"📁 File size: {file_size_mb:.2f} MB")
                    
                    # Handle different file types
                    if uploaded_file.name.endswith('.csv'):
                        # Enhanced CSV reading with error handling
                        try:
                            # Try to read with automatic encoding detection
                            df = pd.read_csv(uploaded_file, encoding='utf-8')
                        except UnicodeDecodeError:
                            try:
                                uploaded_file.seek(0)  # Reset file pointer
                                df = pd.read_csv(uploaded_file, encoding='latin-1')
                                st.warning("📝 File read with Latin-1 encoding due to special characters.")
                            except:
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, encoding='cp1252')
                                st.warning("📝 File read with CP1252 encoding.")
                        except Exception as e:
                            st.error(f"❌ Error reading CSV: {str(e)}")
                            st.stop()
                    
                    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                        # Excel file processing
                        df = pd.read_excel(uploaded_file, engine='openpyxl' if uploaded_file.name.endswith('.xlsx') else 'xlrd')
                        st.success("📊 Excel file processed successfully!")
                    
                    # Data validation and optimization
                    if df is not None and not df.empty:
                        # Memory optimization for large datasets
                        if file_size_mb > 50:  # Large file threshold
                            st.info("⚡ Applying memory optimizations for large dataset...")
                            
                            # Optimize data types
                            for col in df.columns:
                                try:
                                    if df[col].dtype == 'object':
                                        # Try to convert to category if few unique values
                                        if df[col].nunique() / len(df) < 0.5:
                                            df[col] = df[col].astype('category')
                                    elif df[col].dtype == 'int64':
                                        # Downcast integers
                                        df[col] = pd.to_numeric(df[col], downcast='integer')
                                    elif df[col].dtype == 'float64':
                                        # Downcast floats
                                        df[col] = pd.to_numeric(df[col], downcast='float')
                                except:
                                    continue  # Skip problematic columns
                        
                        # Store in session state
                        st.session_state.uploaded_data = df
                        st.session_state.file_name = uploaded_file.name
                        
                        # Clear memory
                        del df
                        gc.collect()
                        
                        st.success(f"✅ File processed: {len(st.session_state.uploaded_data):,} rows × {len(st.session_state.uploaded_data.columns)} columns")
                        st.rerun()
                    else:
                        st.error("❌ File appears to be empty or invalid.")
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.info("💡 Try: Ensure file is properly formatted, check for special characters, or try a smaller sample.")
            
    # Use data from session state with enhanced processing
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
        # Initialize enhanced analyzer and chatbot
        with st.spinner("🔍 Initializing advanced analytics..."):
            analyzer = DataAnalyzer(df)
            chatbot = ChatBot()
        
        # Show enhanced file info in sidebar
        with st.sidebar:
            st.markdown("### 📊 Enhanced File Analytics")
            basic_info = analyzer.get_basic_info()
            
            st.write(f"**Filename:** {st.session_state.file_name}")
            st.write(f"**Rows:** {basic_info['rows']:,}")
            st.write(f"**Columns:** {basic_info['columns']}")
            st.write(f"**Memory:** {basic_info['memory_usage']}")
            st.write(f"**Quality Score:** {basic_info['data_quality_score']:.1f}%")
            
            # Performance indicators
            if basic_info['is_large_dataset']:
                st.warning("⚡ Large Dataset - Optimizations Active")
            else:
                st.success("✅ Standard Processing")
            
            # Memory optimization controls
            with st.expander("🔧 Performance Settings"):
                new_sample_size = st.slider(
                    "Visualization Sample Size",
                    min_value=1000,
                    max_value=min(len(df), 200000),
                    value=st.session_state.file_processing_config['max_sample_size'],
                    step=5000,
                    help="Adjust sample size for visualizations and AI analysis"
                )
                if new_sample_size != st.session_state.file_processing_config['max_sample_size']:
                    st.session_state.file_processing_config['max_sample_size'] = new_sample_size
                    st.rerun()
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            get_text("overview"), 
            get_text("visualizations"), 
            get_text("data_explorer"), 
            get_text("ai_assistant"), 
            get_text("summary")
        ])
        
        with tab1:
            st.markdown("## 📊 Dataset Overview")
            
            # Basic metrics
            basic_info = analyzer.get_basic_info()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{basic_info['rows']:,}</h3>
                    <p>Total Rows</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{basic_info['columns']}</h3>
                    <p>Total Columns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{basic_info['missing_values']:,}</h3>
                    <p>Missing Values</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{basic_info['memory_usage']}</h3>
                    <p>Memory Usage</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Data preview
            st.markdown("### 👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Column information
            st.markdown("### 📋 Column Information")
            column_analysis = analyzer.get_column_analysis()
            
            col_df = pd.DataFrame(column_analysis).T
            col_df = col_df.round(2)
            st.dataframe(col_df, use_container_width=True)
            
            with tab2:
                st.markdown("## 📈 Data Visualizations")
                
                visualizations = create_visualizations(df)
                
                if visualizations:
                    # Create columns for better layout
                    for i, (title, fig) in enumerate(visualizations):
                        st.markdown(f"### {title}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if i < len(visualizations) - 1:
                            st.markdown("---")
                else:
                    st.info("No suitable columns found for visualization. Please ensure your data has numeric or categorical columns.")
            
            with tab3:
                st.markdown("## 🔍 Data Explorer")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🎛️ Filter Options")
                    
                    # Column selector
                    selected_columns = st.multiselect(
                        "Select columns to display:",
                        df.columns.tolist(),
                        default=df.columns.tolist()[:5]
                    )
                    
                    # Row range selector
                    max_rows = len(df)
                    row_range = st.slider(
                        "Select row range:",
                        0, max_rows,
                        (0, min(100, max_rows))
                    )
                
                with col2:
                    st.markdown("### 📊 Quick Stats")
                    if selected_columns:
                        st.write(df[selected_columns].describe())
                
                # Filtered data display
                if selected_columns:
                    st.markdown("### 📋 Filtered Data")
                    filtered_df = df[selected_columns].iloc[row_range[0]:row_range[1]]
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # Download filtered data
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Filtered Data",
                        data=csv,
                        file_name="filtered_data.csv",
                        mime="text/csv"
                    )
            
            with tab4:
                st.markdown(f"## {get_text('ai_assistant')}")
                st.markdown("🤖 **Advanced AI Analysis** - Ask complex questions about your data! AI analyzes your specific dataset with enhanced accuracy.")
                
                # Enhanced response length info with performance indicators
                length_info = {
                    "Short": "💬 Quick 1-2 sentence answers (Fastest)",
                    "Concise": "📋 Clear, focused responses with insights (Recommended)", 
                    "Detailed": "📄 Comprehensive analysis with explanations (Thorough)",
                    "Technical": "🔬 Deep technical analysis with statistics (Expert)"
                }
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**Current Mode:** {length_info[st.session_state.response_length]}")
                with col2:
                    if basic_info['is_large_dataset']:
                        st.warning("⚡ Large Data Mode")
                    else:
                        st.success("✅ Standard Mode")
                
                # Advanced AI features
                with st.expander("🚀 Advanced AI Features"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🤖 Generate Auto Insights", help="Get automatic insights about your dataset"):
                            with st.spinner("🔍 Generating comprehensive insights..."):
                                try:
                                    insights = chatbot.generate_data_insights(df, analyzer)
                                    st.markdown("### 📊 Automatic Dataset Insights")
                                    st.markdown(insights)
                                except Exception as e:
                                    st.error(f"Insight generation failed: {str(e)}")
                    
                    with col2:
                        if st.button("📈 Data Quality Report", help="Get detailed data quality analysis"):
                            with st.spinner("🔍 Analyzing data quality..."):
                                try:
                                    profiling_report = analyzer.get_data_profiling_report()
                                    st.markdown("### 📊 Data Quality Analysis")
                                    
                                    # Show recommendations
                                    if profiling_report['insights']['recommendations']:
                                        st.markdown("**💡 Recommendations:**")
                                        for rec in profiling_report['insights']['recommendations']:
                                            st.markdown(f"- {rec}")
                                    
                                    # Show data insights
                                    insights = profiling_report['insights']
                                    st.markdown(f"**Data Completeness:** {insights['data_completeness']:.1f}%")
                                    st.markdown(f"**Schema Complexity:** {insights['schema_complexity']}")
                                    st.markdown(f"**Size Category:** {insights['size_category']}")
                                    
                                except Exception as e:
                                    st.error(f"Quality analysis failed: {str(e)}")
                
                # Initialize chat history
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                
                # Enhanced chat interface
                user_question = st.text_input(
                    f"💬 {get_text('chat_placeholder')}",
                    placeholder=get_text("chat_placeholder"),
                    help="Ask about patterns, statistics, correlations, outliers, missing data, etc."
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    ask_button = st.button(get_text("ask_ai"), type="primary")
                with col2:
                    clear_chat = st.button("🗑️ Clear Chat")
                
                if clear_chat:
                    st.session_state.chat_history = []
                    st.rerun()
                
                if ask_button and user_question:
                    with st.spinner("🤔 Analyzing your data with advanced AI..."):
                        try:
                            # Generate comprehensive data context
                            data_context = chatbot.generate_comprehensive_data_context(df, analyzer)
                            
                            # Get enhanced AI response
                            response = chatbot.get_response(user_question, data_context, analyzer)
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "question": user_question,
                                "response": response,
                                "timestamp": time.time()
                            })
                            
                            # Clear the input and rerun
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ AI Analysis Error: {str(e)}")
                            st.info("💡 Try: Simplify your question, check internet connection, or try again later.")
                
                # Display chat history with better styling
                if st.session_state.chat_history:
                    st.markdown("### 💬 Chat History")
                    for i, chat in enumerate(reversed(st.session_state.chat_history)):
                        # User message with better contrast
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>🙋‍♂️ You:</strong> {chat['question']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Bot message with better contrast
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <strong>🤖 AI Assistant:</strong> {chat['response']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if i < len(st.session_state.chat_history) - 1:
                            st.markdown("---")
                
                # Quick questions with translations
                st.markdown("### ⚡ Quick Questions")
                
                # Quick questions based on language
                if st.session_state.language == "English":
                    quick_questions = [
                        "What are the key statistics of this dataset?",
                        "Are there any missing values I should be concerned about?",
                        "What patterns do you see in the data?",
                        "Can you suggest some interesting analyses?",
                        "What data quality issues do you notice?"
                    ]
                elif st.session_state.language == "हिंदी":
                    quick_questions = [
                        "इस डेटासेट के मुख्य आँकड़े क्या हैं?",
                        "क्या कोई गुम मूल्य हैं जिनके बारे में मुझे चिंतित होना चाहिए?",
                        "आप डेटा में कौन से पैटर्न देखते हैं?",
                        "आप कुछ दिलचस्प विश्लेषण का सुझाव दे सकते हैं?",
                        "आप कौन सी डेटा गुणवत्ता समस्याएं देखते हैं?"
                    ]
                else:
                    quick_questions = [
                        "What are the key statistics of this dataset?",
                        "Are there any missing values I should be concerned about?",
                        "What patterns do you see in the data?",
                        "Can you suggest some interesting analyses?",
                        "What data quality issues do you notice?"
                    ]
                
                selected_quick = st.selectbox("Choose a quick question:", [""] + quick_questions)
                if selected_quick and st.button("🚀 Ask Quick Question"):
                    data_context = chatbot.generate_data_context(df)
                    with st.spinner("🤔 Analyzing..."):
                        response = chatbot.get_response(selected_quick, data_context)
                    
                    st.session_state.chat_history.append({
                        "question": selected_quick,
                        "response": response
                    })
                    st.rerun()
            
            with tab5:
                st.markdown("## 📋 Data Summary Report")
                
                # Generate comprehensive summary
                basic_info = analyzer.get_basic_info()
                column_analysis = analyzer.get_column_analysis()
                
                st.markdown("### 📊 Executive Summary")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    **Dataset Overview:**
                    - **Total Records:** {basic_info['rows']:,}
                    - **Total Features:** {basic_info['columns']}
                    - **Numeric Columns:** {basic_info['numeric_columns']}
                    - **Categorical Columns:** {basic_info['categorical_columns']}
                    - **Missing Values:** {basic_info['missing_values']:,}
                    - **Memory Usage:** {basic_info['memory_usage']}
                    """)
                
                with col2:
                    # Data quality score
                    missing_ratio = basic_info['missing_values'] / (basic_info['rows'] * basic_info['columns'])
                    quality_score = max(0, 100 - (missing_ratio * 100))
                    
                    st.metric(
                        label="📈 Data Quality Score",
                        value=f"{quality_score:.1f}%",
                        delta=f"{'Excellent' if quality_score > 90 else 'Good' if quality_score > 70 else 'Needs Attention'}"
                    )
                
                # Detailed column summary
                st.markdown("### 📋 Detailed Column Analysis")
                
                for col, info in column_analysis.items():
                    with st.expander(f"📊 {col} ({info['dtype']})"):
                        col_col1, col_col2 = st.columns(2)
                        
                        with col_col1:
                            st.write(f"**Unique Values:** {info['unique_count']:,}")
                            st.write(f"**Missing Values:** {info['null_count']:,} ({info['null_percentage']:.1f}%)")
                        
                        with col_col2:
                            if 'mean' in info:
                                st.write(f"**Mean:** {info['mean']:.2f}")
                                st.write(f"**Std Dev:** {info['std']:.2f}")
                                st.write(f"**Range:** {info['min']:.2f} - {info['max']:.2f}")
                
                # Export summary
                if st.button("📥 Export Summary Report"):
                    summary_data = {
                        'Basic Info': basic_info,
                        'Column Analysis': column_analysis
                    }
                    
                    st.success("✅ Summary report ready for download!")
                    st.json(summary_data)
    
    # Error handling and welcome screen
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>🎯 Welcome to DataViz Pro!</h2>
            <p style="font-size: 1.2rem; color: #666;">
                Upload your CSV file to start exploring your data with advanced analytics and AI insights.
            </p>
            <br>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; max-width: 200px;">
                    <h3>📊 Smart Analytics</h3>
                    <p>Automatic data profiling and insights</p>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; max-width: 200px;">
                    <h3>📈 Beautiful Charts</h3>
                    <p>Interactive visualizations</p>
                </div>
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; color: white; max-width: 200px;">
                    <h3>🤖 AI Assistant</h3>
                    <p>Chat with your data using AI</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()