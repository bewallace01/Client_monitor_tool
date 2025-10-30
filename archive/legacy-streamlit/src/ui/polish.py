"""
UI Polish and Design System
Professional design components, styles, and helpers for consistent UX.
"""

import streamlit as st


# Color Palette - Professional SaaS Design
COLORS = {
    # Primary gradient
    "primary": "#667eea",
    "primary_dark": "#764ba2",

    # Status colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",

    # Neutral palette
    "gray_50": "#f9fafb",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_300": "#d1d5db",
    "gray_400": "#9ca3af",
    "gray_500": "#6b7280",
    "gray_600": "#4b5563",
    "gray_700": "#374151",
    "gray_800": "#1f2937",
    "gray_900": "#111827",

    # Semantic colors
    "background": "#ffffff",
    "surface": "#f9fafb",
    "border": "#e5e7eb",
    "text_primary": "#111827",
    "text_secondary": "#6b7280",

    # Event type colors
    "funding": "#0d6efd",
    "acquisition": "#6610f2",
    "leadership": "#d63384",
    "product": "#fd7e14",
    "partnership": "#20c997",
    "financial": "#198754",
    "award": "#ffc107",
    "regulatory": "#dc3545",
    "news": "#6c757d",
}


def inject_custom_css():
    """Inject comprehensive custom CSS for professional UI."""
    st.markdown(f"""
    <style>
        /* ==================== Global Styles ==================== */

        /* Import professional fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Root variables for consistent theming */
        :root {{
            --primary-color: {COLORS['primary']};
            --primary-dark: {COLORS['primary_dark']};
            --success-color: {COLORS['success']};
            --warning-color: {COLORS['warning']};
            --danger-color: {COLORS['danger']};
            --info-color: {COLORS['info']};
            --border-radius: 8px;
            --border-radius-lg: 12px;
            --transition-speed: 0.2s;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        /* Base typography */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
        }}

        /* ==================== Headers ==================== */

        .main-header {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}

        .subtitle {{
            color: {COLORS['gray_600']};
            font-size: 1.1rem;
            font-weight: 400;
            margin-bottom: 2rem;
            line-height: 1.6;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        /* ==================== Metric Cards ==================== */

        .stMetric {{
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius-lg);
            padding: 1.5rem;
            border: 1px solid {COLORS['border']};
            box-shadow: var(--shadow-md);
            transition: all var(--transition-speed);
        }}

        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}

        .stMetric label {{
            color: {COLORS['text_secondary']};
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stMetric [data-testid="stMetricValue"] {{
            color: {COLORS['text_primary']};
            font-size: 2rem;
            font-weight: 700;
        }}

        .stMetric [data-testid="stMetricDelta"] {{
            font-size: 0.875rem;
            font-weight: 500;
        }}

        /* ==================== Buttons ==================== */

        .stButton > button {{
            border-radius: var(--border-radius);
            font-weight: 500;
            transition: all var(--transition-speed);
            border: 1px solid transparent;
            font-size: 0.95rem;
            padding: 0.5rem 1rem;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            color: white;
        }}

        .stButton > button[kind="secondary"] {{
            background: {COLORS['gray_100']};
            color: {COLORS['text_primary']};
            border-color: {COLORS['border']};
        }}

        /* ==================== Containers ==================== */

        [data-testid="stContainer"] {{
            border-radius: var(--border-radius-lg);
        }}

        /* Container with border */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            border-color: {COLORS['border']} !important;
            border-radius: var(--border-radius-lg) !important;
            transition: all var(--transition-speed);
        }}

        /* ==================== Sidebar ==================== */

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        }}

        [data-testid="stSidebar"] .stMarkdown {{
            color: white;
        }}

        [data-testid="stSidebar"] .stRadio label {{
            color: white !important;
        }}

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label,
        [data-testid="stSidebar"] .stMultiSelect label {{
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500;
        }}

        /* ==================== Forms & Inputs ==================== */

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {{
            border-radius: var(--border-radius);
            border-color: {COLORS['border']};
            transition: all var(--transition-speed);
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {{
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        /* ==================== Tabs ==================== */

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all var(--transition-speed);
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {COLORS['gray_100']};
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            color: white !important;
        }}

        /* ==================== Expanders ==================== */

        .streamlit-expanderHeader {{
            border-radius: var(--border-radius);
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            font-weight: 500;
            transition: all var(--transition-speed);
        }}

        .streamlit-expanderHeader:hover {{
            background-color: {COLORS['gray_100']};
            border-color: {COLORS['primary']};
        }}

        /* ==================== DataFrames ==================== */

        .stDataFrame {{
            border-radius: var(--border-radius-lg);
            overflow: hidden;
        }}

        .stDataFrame [data-testid="stDataFrameResizable"] {{
            border: 1px solid {COLORS['border']};
        }}

        /* ==================== Charts ==================== */

        .plot-container {{
            background: white;
            border-radius: var(--border-radius-lg);
            padding: 1rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid {COLORS['border']};
        }}

        /* ==================== Status Badges ==================== */

        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 500;
            letter-spacing: 0.01em;
        }}

        .status-active {{
            background-color: #d1fae5;
            color: #065f46;
        }}

        .status-inactive {{
            background-color: #fee2e2;
            color: #991b1b;
        }}

        .status-new {{
            background-color: #dbeafe;
            color: #1e40af;
        }}

        .status-reviewed {{
            background-color: #fef3c7;
            color: #92400e;
        }}

        /* ==================== Tooltips ==================== */

        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
            border-bottom: 1px dotted {COLORS['gray_400']};
        }}

        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: {COLORS['gray_900']};
            color: white;
            text-align: center;
            border-radius: var(--border-radius);
            padding: 0.5rem;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity var(--transition-speed);
            font-size: 0.875rem;
        }}

        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}

        /* ==================== Loading States ==================== */

        .loading-skeleton {{
            background: linear-gradient(
                90deg,
                {COLORS['gray_200']} 25%,
                {COLORS['gray_100']} 50%,
                {COLORS['gray_200']} 75%
            );
            background-size: 200% 100%;
            animation: loading 1.5s ease-in-out infinite;
            border-radius: var(--border-radius);
        }}

        @keyframes loading {{
            0% {{
                background-position: 200% 0;
            }}
            100% {{
                background-position: -200% 0;
            }}
        }}

        /* ==================== Empty States ==================== */

        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: {COLORS['text_secondary']};
        }}

        .empty-state-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}

        .empty-state-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {COLORS['text_primary']};
            margin-bottom: 0.5rem;
        }}

        .empty-state-description {{
            font-size: 1rem;
            margin-bottom: 2rem;
        }}

        /* ==================== Animations ==================== */

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .fade-in {{
            animation: fadeIn 0.3s ease-out;
        }}

        @keyframes slideIn {{
            from {{
                transform: translateX(-10px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        .slide-in {{
            animation: slideIn 0.3s ease-out;
        }}

        /* ==================== Utility Classes ==================== */

        .text-primary {{
            color: {COLORS['primary']} !important;
        }}

        .text-success {{
            color: {COLORS['success']} !important;
        }}

        .text-warning {{
            color: {COLORS['warning']} !important;
        }}

        .text-danger {{
            color: {COLORS['danger']} !important;
        }}

        .bg-surface {{
            background-color: {COLORS['surface']} !important;
        }}

        .border-primary {{
            border-color: {COLORS['primary']} !important;
        }}

        /* ==================== Responsive Design ==================== */

        @media (max-width: 768px) {{
            .main-header {{
                font-size: 2rem;
            }}

            .subtitle {{
                font-size: 1rem;
            }}

            .stMetric [data-testid="stMetricValue"] {{
                font-size: 1.5rem;
            }}
        }}

        /* ==================== Print Styles ==================== */

        @media print {{
            [data-testid="stSidebar"] {{
                display: none;
            }}

            .stButton {{
                display: none;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_tooltip(text: str, tooltip_text: str) -> str:
    """
    Render text with a tooltip.

    Args:
        text: The main text to display
        tooltip_text: The tooltip text to show on hover

    Returns:
        HTML string with tooltip
    """
    return f"""
    <div class="tooltip">{text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """


def render_empty_state(icon: str, title: str, description: str, action_text: str = None, action_callback=None):
    """
    Render a beautiful empty state.

    Args:
        icon: Emoji or icon to display
        title: Main title
        description: Description text
        action_text: Optional action button text
        action_callback: Optional callback for action button
    """
    html = f"""
    <div class="empty-state fade-in">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if action_text and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_text, use_container_width=True, type="primary"):
                action_callback()


def render_loading_skeleton(height: str = "100px", width: str = "100%"):
    """
    Render a loading skeleton placeholder.

    Args:
        height: Height of the skeleton
        width: Width of the skeleton
    """
    st.markdown(f"""
    <div class="loading-skeleton" style="height: {height}; width: {width};"></div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str, text: str = None) -> str:
    """
    Render a status badge.

    Args:
        status: Status type (active, inactive, new, reviewed, etc.)
        text: Optional custom text (defaults to status)

    Returns:
        HTML string with status badge
    """
    display_text = text or status.capitalize()
    return f'<span class="status-badge status-{status.lower()}">{display_text}</span>'


def get_event_type_badge(event_type: str) -> str:
    """
    Get a styled badge for an event type.

    Args:
        event_type: Event type

    Returns:
        HTML string with colored badge
    """
    emoji_map = {
        'funding': '💰',
        'acquisition': '🤝',
        'leadership': '👤',
        'product': '🚀',
        'partnership': '🤝',
        'financial': '💵',
        'award': '🏆',
        'regulatory': '⚖️',
        'news': '📰',
        'other': '📌'
    }

    color = COLORS.get(event_type.lower(), COLORS['news'])
    emoji = emoji_map.get(event_type.lower(), '📌')

    return f"""
    <span style="background-color: {color}; color: white; padding: 4px 12px;
                 border-radius: 6px; font-size: 0.85em; font-weight: 500;">
        {emoji} {event_type.upper()}
    </span>
    """


def render_page_header(title: str, subtitle: str = None, icon: str = None):
    """
    Render a consistent page header.

    Args:
        title: Page title
        subtitle: Optional subtitle
        icon: Optional icon/emoji
    """
    header_text = f"{icon} {title}" if icon else title
    st.markdown(f'<h1 class="main-header">{header_text}</h1>', unsafe_allow_html=True)

    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)


def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """
    Render an info card with icon.

    Args:
        title: Card title
        content: Card content
        icon: Icon/emoji
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['info']}15 0%, {COLORS['info']}05 100%);
                border-left: 4px solid {COLORS['info']};
                padding: 1rem;
                border-radius: var(--border-radius);
                margin: 1rem 0;">
        <div style="font-size: 1.5em; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: {COLORS['text_primary']};">{title}</div>
        <div style="color: {COLORS['text_secondary']};">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_success_card(title: str, content: str, icon: str = "✅"):
    """Render a success card."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['success']}15 0%, {COLORS['success']}05 100%);
                border-left: 4px solid {COLORS['success']};
                padding: 1rem;
                border-radius: var(--border-radius);
                margin: 1rem 0;">
        <div style="font-size: 1.5em; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: {COLORS['text_primary']};">{title}</div>
        <div style="color: {COLORS['text_secondary']};">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_warning_card(title: str, content: str, icon: str = "⚠️"):
    """Render a warning card."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['warning']}15 0%, {COLORS['warning']}05 100%);
                border-left: 4px solid {COLORS['warning']};
                padding: 1rem;
                border-radius: var(--border-radius);
                margin: 1rem 0;">
        <div style="font-size: 1.5em; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: {COLORS['text_primary']};">{title}</div>
        <div style="color: {COLORS['text_secondary']};">{content}</div>
    </div>
    """, unsafe_allow_html=True)
