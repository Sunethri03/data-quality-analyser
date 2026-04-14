import auth
import database
import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

database.create_user_table()
menu = ["Login", "Signup"]

choice = st.sidebar.selectbox("Account", menu)
if choice == "Signup":

    st.subheader("Create New Account")

    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")

    if st.button("Signup"):
        auth.add_user(new_user, new_password)
        st.success("Account created successfully")
        st.info("Go to Login menu")
elif choice == "Login":

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        result = auth.login_user(username, password)

        if result:
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid username or password")

# Custom Styling
st.markdown(
    """
    <style>
    body {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)


st.set_page_config(
    page_title="Data Quality Analyser", layout="wide", initial_sidebar_state="expanded"
)

st.title("📊 Data Quality Analyser")
st.markdown("### Intelligent Dataset Audit & Integrity Scoring System")

st.write("Upload a CSV or Excel file to check dataset quality")
st.markdown("---")
# ===============================
# SIDEBAR BRANDING
# ===============================

st.sidebar.markdown("## 🏢 Data Quality Analyser")
st.sidebar.markdown("Intelligent Dataset Audit System")
st.sidebar.markdown("### Platform Info")

st.sidebar.write("Version: 1.2")
st.sidebar.write("Developer: Sunethri")

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
🚀 Features

• Data Quality Audit  
• ML Preprocessing Insights  
• Dataset Adequacy Detection  
• Interactive Data Dashboard  
• Automated Integrity Scoring  
• Professional PDF Reports
"""
)
if st.session_state.logged_in:

    uploaded_file = st.file_uploader(
        "Upload your dataset (CSV or Excel format)", type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:

        # Read file depending on extension
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("Dataset uploaded successfully!")

        # ===============================
        # TARGET COLUMN ANALYSIS
        # ===============================

        st.subheader("🎯 Target Column Analysis")

        target_column = st.selectbox(
            "Select Target Column (Optional for ML Analysis)",
            ["None"] + list(df.columns),
        )
        if target_column != "None":

            st.markdown("### Class Distribution")

            class_counts = df[target_column].value_counts()

            fig = px.bar(
                x=class_counts.index,
                y=class_counts.values,
                labels={"x": "Class", "y": "Count"},
                title="Target Class Distribution",
            )

            st.plotly_chart(fig, use_container_width=True)

            imbalance_ratio = class_counts.max() / class_counts.min()

            if imbalance_ratio > 3:
                st.warning(
                    "⚠ Class imbalance detected. Consider resampling techniques like SMOTE."
                )
            else:
                st.success("Class distribution looks balanced.")

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        st.subheader("Dataset Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("📄 Rows", f"{df.shape[0]:,}")
        col2.metric("📊 Columns", f"{df.shape[1]:,}")
        col3.metric("⚠ Total Missing", f"{df.isnull().sum().sum():,}")

        # ===============================
        # DATASET ADEQUACY CHECK
        # ===============================

        st.subheader("Dataset Adequacy Check")

        adequacy_penalty = 0
        adequacy_severity = "Low"

        if df.shape[0] < 100:
            adequacy_penalty += 10
            adequacy_severity = "Moderate"
            st.warning("Small dataset: Less than 100 rows may affect ML performance.")

        if df.shape[1] > df.shape[0]:
            adequacy_penalty += 10
            adequacy_severity = "High"
            st.warning("High feature-to-sample ratio: Risk of overfitting.")

        if adequacy_penalty == 0:
            st.success("Dataset size appears sufficient for analysis.")

        st.subheader("Missing Values Analysis")

        missing_count = df.isnull().sum()
        missing_percent = (missing_count / len(df)) * 100

        missing_df = pd.DataFrame(
            {
                "Missing Count": missing_count,
                "Missing Percentage (%)": missing_percent.round(2),
            }
        )

        st.dataframe(missing_df)
        st.subheader("Duplicate Rows Analysis")

        duplicate_count = df.duplicated().sum()
        total_rows = len(df)
        duplicate_percent = (duplicate_count / total_rows) * 100

        st.write(f"Duplicate Rows: {duplicate_count}")
        st.write(f"Duplicate Percentage: {duplicate_percent:.2f}%")

        if duplicate_count == 0:
            st.success("No duplicate rows detected.")
        elif duplicate_percent <= 5:
            st.warning("Low level of duplicate rows detected.")
        else:
            st.error(
                "High duplicate density detected. Structural integrity risk present."
            )

            st.subheader("Column Structure Analysis")

        column_info = []

        for col in df.columns:
            dtype = df[col].dtype
            unique_values = df[col].nunique()

            if df[col].dtype == "object":
                role = "Categorical (Text)"
            elif unique_values < 10:
                role = "Categorical (Low Cardinality)"
            else:
                role = "Numeric / Continuous"

            column_info.append(
                {
                    "Column Name": col,
                    "Data Type": str(dtype),
                    "Unique Values": unique_values,
                    "Detected Role": role,
                }
            )

            column_df = pd.DataFrame(column_info)

            st.dataframe(column_df)
        # ===============================
        # DATA VISUALIZATION DASHBOARD
        # ===============================

        st.subheader("📊 Data Quality Visualization")

        # Missing Values Heatmap
        st.markdown("### Missing Values Heatmap")

        plt.figure(figsize=(10, 5))
        sns.heatmap(df.isnull(), cbar=False)
        st.pyplot(plt)

        # ===============================
        # Missing Value Percentage Chart
        # ===============================

        st.markdown("### Missing Values Percentage")

        missing_percent = (df.isnull().sum() / len(df)) * 100

        fig = px.bar(
            x=missing_percent.index,
            y=missing_percent.values,
            labels={"x": "Column", "y": "Missing %"},
            title="Missing Data Percentage by Column",
        )

        st.plotly_chart(fig, use_container_width=True)

        # Correlation Heatmap
        st.markdown("### Feature Correlation")

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        if len(numeric_df.columns) > 1:
            plt.figure(figsize=(8, 6))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
            st.pyplot(plt)
        else:
            st.info("Not enough numeric columns for correlation heatmap.")
            st.subheader("Outlier Detection (Numeric Columns)")

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

        outlier_results = []

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            outlier_results.append(
                {
                    "Column": col,
                    "Outlier Count": len(outliers),
                    "Lower Bound": round(lower_bound, 2),
                    "Upper Bound": round(upper_bound, 2),
                }
            )

        outlier_df = pd.DataFrame(outlier_results)

        st.dataframe(outlier_df)

        # ===============================
        # INTERACTIVE DATA DASHBOARD
        # ===============================

        st.subheader("📈 Interactive Dataset Dashboard")

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

        if len(numeric_cols) > 0:

            selected_feature = st.selectbox(
                "Select Feature for Distribution", numeric_cols
            )

            fig = px.histogram(df, x=selected_feature, nbins=30)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No numeric features available for visualization.")

        # ===============================
        # ML DATA PREPROCESSING INSIGHTS
        # ===============================

        st.subheader("🧠 ML Preprocessing Insights")

        # -------- DATA TYPE CHECK --------
        st.markdown("### Data Type Validation")

        dtype_issues = []

        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    pd.to_numeric(df[col])
                    dtype_issues.append((col, "Object", "Numeric"))
                except:
                    try:
                        pd.to_datetime(df[col])
                        dtype_issues.append((col, "Object", "Datetime"))
                    except:
                        pass

        if dtype_issues:

            dtype_df = pd.DataFrame(
                dtype_issues, columns=["Column", "Current Type", "Suggested Type"]
            )

            st.dataframe(dtype_df)

            example_col = dtype_issues[0][0]
            st.code(
                f"df['{example_col}'] = pd.to_numeric(df['{example_col}'], errors='coerce')",
                language="python",
            )
        else:
            st.success("No obvious datatype issues detected.")

        # -------- CATEGORICAL ENCODING --------
        st.markdown("### Categorical Encoding Suggestions")

        categorical_cols = df.select_dtypes(include=["object"]).columns

        if len(categorical_cols) > 0:
            encoding_info = []

            for col in categorical_cols:
                unique_vals = df[col].nunique()

                if unique_vals <= 10:
                    method = "One-Hot Encoding"
                else:
                    method = "Label Encoding"

                encoding_info.append((col, unique_vals, method))

            encoding_df = pd.DataFrame(
                encoding_info, columns=["Column", "Unique Values", "Suggested Encoding"]
            )

            st.dataframe(encoding_df)

            example_cat = categorical_cols[0]

            st.code(f"pd.get_dummies(df, columns=['{example_cat}'])", language="python")

        else:
            st.success("No categorical columns detected.")

        # -------- FEATURE SCALING --------
        st.markdown("### Feature Scaling Recommendation")

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

        if len(numeric_cols) > 0:
            st.write("Scaling recommended for numeric features before ML models.")

            st.code(
                "from sklearn.preprocessing import StandardScaler\n"
                "scaler = StandardScaler()\n"
                "df[numeric_cols] = scaler.fit_transform(df[numeric_cols])",
                language="python",
            )
        else:
            st.info("No numeric columns detected for scaling.")

        # ===============================
        # PROFESSIONAL AUDIT SCORING
        # ===============================

        # ---- COMPLETENESS (Missing Values) ----
        total_cells = df.shape[0] * df.shape[1]
        total_missing = df.isnull().sum().sum()
        missing_percent = (total_missing / total_cells) * 100

        if missing_percent <= 5:
            completeness_penalty = 0
        elif missing_percent <= 10:
            completeness_penalty = 8
        elif missing_percent <= 20:
            completeness_penalty = 18
        elif missing_percent <= 35:
            completeness_penalty = 30
        else:
            completeness_penalty = 45

        # ---- STRUCTURAL INTEGRITY (Duplicates) ----
        duplicate_count = df.duplicated().sum()
        duplicate_percent = (duplicate_count / len(df)) * 100

        if duplicate_percent == 0:
            structural_penalty = 0
        elif duplicate_percent <= 3:
            structural_penalty = 4
        elif duplicate_percent <= 10:
            structural_penalty = 15
        elif duplicate_percent <= 20:
            structural_penalty = 25
        else:
            structural_penalty = 35
        # ---- STATISTICAL STABILITY (Outliers) ----
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

        # Exclude identifier-like columns
        refined_numeric_cols = []

        for col in numeric_cols:
            is_id_name = "id" in col.lower()
            is_unique = df[col].nunique() == len(df)
            is_low_cardinality = df[col].nunique() < 10

            if not is_id_name and not is_unique and not is_low_cardinality:
                refined_numeric_cols.append(col)

        numeric_cols = refined_numeric_cols

        outlier_count = 0
        total_numeric_values = 0

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            col_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()

            outlier_count += col_outliers
            total_numeric_values += df[col].count()

        if total_numeric_values > 0:
            outlier_percent = (outlier_count / total_numeric_values) * 100
        else:
            outlier_percent = 0

        if outlier_percent < 1:
            statistical_penalty = 0
        elif outlier_percent <= 4:
            statistical_penalty = 5
        elif outlier_percent <= 8:
            statistical_penalty = 12
        else:
            statistical_penalty = 20

        # ---- FINAL AUDIT SCORE ----

        audit_score = 100 - (
            completeness_penalty
            + structural_penalty
            + statistical_penalty
            + adequacy_penalty
        )
        if audit_score < 0:
            audit_score = 0

        # ===============================
        # ML READINESS SCORE
        # ===============================

        ml_score = 100

        if missing_percent > 20:
            ml_score -= 20

        if duplicate_percent > 5:
            ml_score -= 15

        if outlier_percent > 10:
            ml_score -= 15

        if adequacy_penalty > 0:
            ml_score -= 10

        st.subheader("🤖 ML Readiness Score")

        st.metric("ML Readiness", f"{ml_score} / 100")

        if ml_score > 80:
            st.success("Dataset is well prepared for machine learning.")
        elif ml_score > 60:
            st.warning("Dataset usable but preprocessing recommended.")
        else:
            st.error("Dataset requires significant cleaning before ML.")

        # ===============================
        # SEVERITY CLASSIFICATION
        # ===============================

        # Completeness Severity
        if completeness_penalty == 0:
            completeness_severity = "Low"
        elif completeness_penalty <= 25:
            completeness_severity = "Moderate"
        else:
            completeness_severity = "High"

        # Structural Severity
        if structural_penalty == 0:
            structural_severity = "Low"
        elif structural_penalty <= 20:
            structural_severity = "Moderate"
        else:
            structural_severity = "High"

        # Statistical Severity
        if statistical_penalty == 0:
            statistical_severity = "Low"
        elif statistical_penalty <= 10:
            statistical_severity = "Moderate"
        else:
            statistical_severity = "High"
        # ===============================
        # RISK BREAKDOWN TABLE
        # ===============================
        # ===============================
        # EXECUTIVE SUMMARY (Dynamic)
        # ===============================

        st.subheader("🧠 Executive Summary")

        # Determine highest penalty category
        penalties = {
            "Completeness": completeness_penalty,
            "Structural Integrity": structural_penalty,
            "Statistical Stability": statistical_penalty,
        }

        highest_category = max(penalties, key=penalties.get)
        highest_penalty = penalties[highest_category]

        # Generate dynamic summary
        summary_points = []

        if completeness_penalty > 0:
            summary_points.append("Missing data detected.")

        if structural_penalty > 0:
            summary_points.append("Duplicate records present.")

        if statistical_penalty > 0:
            summary_points.append("Outliers may affect modeling stability.")

        if adequacy_penalty > 0:
            summary_points.append("Dataset size or structure may limit generalization.")

        if not summary_points:
            summary_points.append("Dataset appears clean and ML-ready.")

        summary_text = " ".join(summary_points)

        st.info(summary_text)

        st.subheader("Risk Breakdown")

        breakdown_df = pd.DataFrame(
            {
                "Category": [
                    "Completeness",
                    "Structural Integrity",
                    "Statistical Stability",
                    "Dataset Adequacy",
                ],
                "Penalty (Points)": [
                    f"{completeness_penalty} / 45",
                    f"{structural_penalty} / 35",
                    f"{statistical_penalty} / 20",
                    f"{adequacy_penalty} / 20",
                ],
                "Severity": [
                    completeness_severity,
                    structural_severity,
                    statistical_severity,
                    adequacy_severity,
                ],
            }
        )
        st.dataframe(breakdown_df)

        # ===============================
        # AUTO DATA CLEANING PIPELINE
        # ===============================

        st.subheader("🧹 Suggested Data Cleaning Pipeline")

        pipeline = []

        if missing_percent > 0:
            pipeline.append("Fill missing values using median/mode.")

        if duplicate_percent > 0:
            pipeline.append("Remove duplicate rows.")

        if outlier_percent > 5:
            pipeline.append("Apply IQR outlier removal.")

        if len(pipeline) == 0:
            st.success("Dataset appears clean. No major preprocessing required.")
        else:
            for step in pipeline:
                st.write("•", step)

        # ===============================
        # REMEDIATION SUGGESTIONS
        # ===============================

        st.subheader("Remediation Suggestions")

        # ---- Completeness Remediation ----
        if completeness_severity in ["Moderate", "High"]:
            with st.expander("View Completeness Remediation (Missing Values)"):
                st.write("Recommended Pandas Example:")

                example_numeric_cols = numeric_cols
                categorical_cols = df.select_dtypes(include=["object"]).columns

                if len(numeric_cols) > 0:
                    example_col = numeric_cols[0]
                    st.code(
                        f"# Median Imputation for numeric column\n"
                        f"df['{example_col}'] = df['{example_col}'].fillna(df['{example_col}'].median())",
                        language="python",
                    )

                if len(categorical_cols) > 0:
                    example_cat = categorical_cols[0]
                    st.code(
                        f"# Mode Imputation for categorical column\n"
                        f"df['{example_cat}'] = df['{example_cat}'].fillna(df['{example_cat}'].mode()[0])",
                        language="python",
                    )
        # ---- Structural Integrity Remediation ----
        if structural_severity in ["Moderate", "High"]:
            with st.expander("View Structural Remediation (Duplicates)"):
                st.write("Recommended Pandas Example:")
                st.code(
                    "# Remove duplicate rows\n" "df = df.drop_duplicates()",
                    language="python",
                )

        # ---- Statistical Stability Remediation ----
        if statistical_severity in ["Moderate", "High"]:
            with st.expander("View Statistical Remediation (Outliers)"):

                st.write("Option 1: Remove Outliers (IQR Method)")
                example_numeric_cols = numeric_cols

                if len(example_numeric_cols) > 0:
                    example_col = example_numeric_cols[0]

                    st.code(
                        f"# Remove outliers using IQR method for column '{example_col}'\n"
                        f"Q1 = df['{example_col}'].quantile(0.25)\n"
                        f"Q3 = df['{example_col}'].quantile(0.75)\n"
                        f"IQR = Q3 - Q1\n"
                        f"lower = Q1 - 1.5 * IQR\n"
                        f"upper = Q3 + 1.5 * IQR\n"
                        f"df = df[(df['{example_col}'] >= lower) & (df['{example_col}'] <= upper)]",
                        language="python",
                    )

                    st.write("Option 2: Cap Outliers (Winsorization Style)")

                    st.code(
                        f"# Cap extreme values instead of removing\n"
                        f"Q1 = df['{example_col}'].quantile(0.25)\n"
                        f"Q3 = df['{example_col}'].quantile(0.75)\n"
                        f"IQR = Q3 - Q1\n"
                        f"lower = Q1 - 1.5 * IQR\n"
                        f"upper = Q3 + 1.5 * IQR\n"
                        f"df['{example_col}'] = df['{example_col}'].clip(lower,  upper)",
                        language="python",
                    )

        # ---- DISPLAY SCORE ----
        st.markdown("## 📊 Overall Integrity Score")

        score_color = (
            "green" if audit_score >= 85 else "orange" if audit_score >= 70 else "red"
        )

        st.markdown(
            f"<h1 style='text-align:center; color:{score_color};'>{audit_score} /  100</h1>",
            unsafe_allow_html=True,
        )
        if audit_score >= 85:
            overall_risk = "Low Risk"
        elif audit_score >= 70:
            overall_risk = "Moderate Risk"
        elif audit_score >= 50:
            overall_risk = "High Risk"
        else:
            overall_risk = "Critical Risk"

        st.markdown(f"**Overall Risk Level:** {overall_risk}")
        st.markdown("---")

        # ===============================
        # DOWNLOADABLE PDF AUDIT REPORT
        # ===============================

        st.subheader("Download Professional Audit Report (PDF)")

        def generate_pdf(
            audit_score,
            summary_text,
            completeness_penalty,
            structural_penalty,
            statistical_penalty,
            adequacy_penalty,
            completeness_severity,
            structural_severity,
            statistical_severity,
            adequacy_severity,
        ):

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            elements = []

            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            normal_style = styles["Normal"]

            elements.append(Paragraph("Data Integrity Audit Report", title_style))
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(
                Paragraph(f"<b>Integrity Score:</b> {audit_score} / 100", normal_style)
            )

            # Risk Level
            if audit_score >= 85:
                risk_level = "Low Risk"
            elif audit_score >= 70:
                risk_level = "Moderate Risk"
            elif audit_score >= 50:
                risk_level = "High Risk"
            else:
                risk_level = "Critical Risk"

            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph(f"<b>Risk Level:</b> {risk_level}", normal_style))

            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("<b>Executive Summary:</b>", normal_style))
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph(summary_text, normal_style))
            elements.append(Spacer(1, 0.3 * inch))

            data = [
                ["Category", "Penalty", "Severity"],
                ["Completeness", f"{completeness_penalty} / 45", completeness_severity],
                [
                    "Structural Integrity",
                    f"{structural_penalty} / 35",
                    structural_severity,
                ],
                [
                    "Statistical Stability",
                    f"{statistical_penalty} / 20",
                    statistical_severity,
                ],
                ["Dataset Adequacy", f"{adequacy_penalty} / 20", adequacy_severity],
            ]

            table = Table(data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])

            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ]
                )
            )

            elements.append(table)

            doc.build(elements)
            buffer.seek(0)

            return buffer

        # Generate PDF
        pdf_file = generate_pdf(
            audit_score,
            summary_text,
            completeness_penalty,
            structural_penalty,
            statistical_penalty,
            adequacy_penalty,
            completeness_severity,
            structural_severity,
            statistical_severity,
            adequacy_severity,
        )

        # Download Button
        st.download_button(
            label="Download Audit Report (PDF)",
            data=pdf_file,
            file_name="Data_Integrity_Audit_Report.pdf",
            mime="application/pdf",
        )
