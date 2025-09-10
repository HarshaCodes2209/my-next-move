import io
from flask import Flask, request, jsonify, render_template, send_file
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# Imports for PDF Resume Generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# --- NEW IMPORTS FOR CUSTOM FONTS ---
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Main Flask App Initialization ---
app = Flask(__name__)


# ==============================================================================
# --- CHATBOT AND AI SETUP (LangChain & Groq) ---
# ==============================================================================

# Setup Groq - IMPORTANT: Replace with your actual key or use environment variables
groq_api_key = "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"
model = 'llama-3.1-8b-instant'  # or any other available model
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

system_prompt = "You are a friendly conversational chatbot"
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

# Prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{human_input}"),
])

# Conversation object for the chatbot
conversation = LLMChain(
    llm=groq_chat,
    prompt=prompt,
    memory=memory,
    verbose=False
)


# ==============================================================================
# --- STANDARD AND CHATBOT FLASK ROUTES ---
# ==============================================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ai")
def ai():
    return render_template("ai.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/inspire")
def inspire():
    return render_template("inspiration.html")

@app.route("/feedback")
def feedback():
    return render_template("example.html")

@app.route("/resume")
def resume():
    """Renders the page with the resume form."""
    return render_template("resume.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please enter a message."})
    try:
        response = conversation.predict(human_input=user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})


# ==============================================================================
# --- PDF RESUME GENERATION ROUTE (WITH CUSTOM FONTS) ---
# ==============================================================================

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    # Collect form data
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    linkedin = request.form.get("linkedin")
    skills = request.form.get("skills")
    education = request.form.get("education")
    experience = request.form.get("experience")
    achievements = request.form.get("achievements")

    # --- AI Content Generation Step ---
    try:
        resume_generation_prompt = f"""
        Act as a professional resume writer. Generate complete and enhanced resume content based on the details below.
        Follow these instructions:
        1. **Create a professional summary:** Write a 2-3 sentence summary.
        2. **Format sections:** Use these exact section titles: **Summary**, **Skills**, **Experience**, **Education**, **Achievements**.
        3. **Use specific formatting:** Section titles MUST be in double asterisks. Every list item MUST start with a bullet (•).
        4. **Enhance content:** Rewrite experience and achievement points to start with strong action verbs. Quantify results. Do not invent new information.
        5. **Exclude contact info:** Do not add the name, email, or phone to your generated text.
        
        Raw information:
        - Experience: {experience}
        - Skills: {skills}
        - Education: {education}
        - Achievements: {achievements}
        """
        ai_response = groq_chat.invoke([HumanMessage(content=resume_generation_prompt)])
        ai_resume = ai_response.content
    except Exception as e:
        print(f"AI generation failed: {e}")
        ai_resume = f"**Summary**\nFailed to generate AI content.\n**Skills**\n{skills}\n**Experience**\n{experience}\n**Education**\n{education}\n**Achievements**\n{achievements}"

    # --- PDF Generation with Custom Fonts ---
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- NEW: REGISTER CUSTOM FONTS ---
    try:
        pdfmetrics.registerFont(TTFont('Anton', 'Anton-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lexend', 'Lexend-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lexend-Bold', 'Lexend-Bold.ttf'))
        
        # Define font names to use throughout the document
        header_font = 'Anton'
        body_font = 'Lexend'
        body_font_bold = 'Lexend-Bold'
    except Exception as e:
        print(f"FONT ERROR: Could not load custom fonts. Ensure .ttf files are in the correct directory. Error: {e}")
        # Fallback to default fonts if custom ones aren't found
        header_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
        body_font_bold = 'Helvetica-Bold'


    # --- Define Color Palette ---
    bg_color = colors.HexColor('#1C1C1C')
    accent_color = colors.HexColor('#DA291C')
    primary_text_color = colors.HexColor('#FFFFFF')

    # Draw Background
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    margin = 0.75 * inch
    
    # Redesigned Header with custom font
    c.setFillColor(accent_color)
    c.rect(0, height - (1.5 * inch), width, 1.5 * inch, stroke=0, fill=1)
    
    c.setFillColor(primary_text_color)
    c.setFont(header_font, 36) # USE CUSTOM FONT
    c.drawString(margin, height - 0.9 * inch, name)

    c.setFont(body_font, 10) # USE CUSTOM FONT
    c.setFillColor(primary_text_color)
    contact_line = f"{email}  |  {phone}"
    if linkedin:
        contact_line += f"  |  {linkedin}"
    c.drawString(margin, height - 1.2 * inch, contact_line)
    
    # --- Main Content Area ---
    y = height - 2 * inch
    x_main = margin
    main_content_width = width - (2 * margin)

    # --- Define Styles with Custom Fonts ---
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='Normal_Custom',
        parent=styles['Normal'],
        fontName=body_font, # USE CUSTOM FONT
        fontSize=10,
        textColor=primary_text_color,
        leading=16,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle', 
        fontName=header_font, # USE CUSTOM FONT
        fontSize=14, 
        textColor=accent_color,
        spaceAfter=10,
        spaceBefore=14
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeading', 
        fontName=body_font_bold, # USE CUSTOM FONT
        fontSize=11, 
        textColor=primary_text_color,
        spaceAfter=6
    ))

    # --- Loop through AI resume content and draw to PDF ---
    for line in ai_resume.split("\n"):
        line = line.strip()
        if not line: continue

        style = styles['Normal_Custom']
        if line.startswith("**") and line.endswith("**"):
            style = styles['SectionTitle']
            line = line.replace("**", "")
        elif "|" in line and ("Present" in line or any(char.isdigit() for char in line)):
            style = styles['SubHeading']

        p = Paragraph(line, style)
        w, h = p.wrapOn(c, main_content_width, height)
        
        if y < (height - 2 * inch): y -= style.spaceBefore
        if y - h < margin:
            c.showPage()
            c.setFillColor(bg_color); c.rect(0, 0, width, height, stroke=0, fill=1)
            c.setFillColor(accent_color); c.rect(0, height - (1.5 * inch), width, 1.5 * inch, stroke=0, fill=1)
            c.setFillColor(primary_text_color); c.setFont(header_font, 36); c.drawString(margin, height - 0.9 * inch, name)
            c.setFont(body_font, 10); c.drawString(margin, height - 1.2 * inch, contact_line)
            y = height - 2 * inch

        p.drawOn(c, x_main, y - h)
        y -= (h + style.spaceAfter)

        if style.name == 'SectionTitle':
            line_y = y + style.spaceAfter - 4
            c.setStrokeColor(accent_color)
            c.setLineWidth(1)
            c.line(x_main, line_y, x_main + 2.5 * inch, line_y)

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{name.replace(' ', '_')}_Resume_Modern.pdf", mimetype="application/pdf")

# ==============================================================================
# --- MAIN EXECUTION BLOCK ---
# ==============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
