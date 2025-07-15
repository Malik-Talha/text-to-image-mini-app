from io import BytesIO
import streamlit as st
import os
import uuid
from datetime import datetime
from PIL import Image
import time
import json

from config import settings
from database import Database
from models import ImageRecord, FeedbackData
from services.image_generator import ImageGenerator

# Page configuration
st.set_page_config(
    page_title="🎨 Text-to-Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .image-card {
        background: white;
        border-radius: 1rem;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .prompt-text {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .meta-info {
        color: #718096;
        font-size: 0.9em;
    }
    
    .style-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8em;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'image_generator' not in st.session_state:
    st.session_state.image_generator = ImageGenerator()

if "view" not in st.session_state:
    st.session_state.view = "main"
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Create images directory
os.makedirs(settings.IMAGES_DIR, exist_ok=True)

if st.session_state.view == "main":

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Text-to-Image Generator</h1>
        <p>Create stunning images from your imagination using AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Database connection status
        if st.session_state.db.collection is not None:
            st.success("✅ MongoDB Connected")
        else:
            st.error("❌ MongoDB Disconnected")
        
        # Statistics
        if st.session_state.db.collection is not None:
            total_images = st.session_state.db.count_images()
            st.metric("Total Images", total_images)
        
        # Settings
        st.header("⚙️ Settings")
        gallery_limit = st.slider("Gallery Size", 5, 50, 20)
        
        # View options
        st.header("👁️ View Options")
        view_mode = st.selectbox("View Mode", ["Gallery", "Prompt History", "Statistics"])

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🎨 Generate Image")
        
        with st.form("image_generation_form"):
            prompt = st.text_area(
                "Describe your image:",
                placeholder="A majestic dragon flying over a mystical forest at sunset...",
                height=100
            )
            
            style = st.selectbox(
                "Art Style:",
                options=list(settings.STYLES.keys()),
                format_func=lambda x: x.title()
            )
            
            submitted = st.form_submit_button("🚀 Generate Image")
            
            if submitted and prompt:
                try:
                    with st.spinner("🎨 Generating your image... This may take 30-60 seconds."):
                        start_time = time.time()
                        
                        # Generate image
                        image_data = st.session_state.image_generator.generate_image(prompt, style)
                        
                        # Calculate generation time
                        generation_time = time.time() - start_time
                        st.session_state.generation_time = generation_time

                        # Save in session state
                        st.session_state.last_image = image_data
                        st.session_state.last_prompt = prompt
                        st.session_state.style=style

                        # Switch to feedback view
                        st.session_state.view = "feedback"
                        st.success(f"✅ Image generated successfully in {generation_time:.1f}s!")
                        st.balloons()
                        st.rerun()
                        
                        # # Save image
                        # image_id = str(uuid.uuid4())
                        # filename = f"{image_id}.png"
                        # filepath = os.path.join(settings.IMAGES_DIR, filename)
                        
                        # with open(filepath, "wb") as f:
                        #     f.write(image_data)
                        
                        # # Get file size
                        # file_size = os.path.getsize(filepath)
                        
                        # # Create record
                        # image_record = ImageRecord(
                        #     id=image_id,
                        #     prompt=prompt,
                        #     expected_style=style,
                        #     filename=filename,
                        #     created_at=datetime.now(),
                        #     generation_time=generation_time,
                        #     status="completed",
                        #     file_size=file_size
                        # )
                        
                        # # Save to database
                        # st.session_state.db.save_image_record(image_record)
                        
                        # st.success(f"✅ Image generated successfully in {generation_time:.1f}s!")
                        # st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ Error generating image: {str(e)}")
            
            elif submitted and not prompt:
                st.error("❌ Please enter a prompt description.")

    with col2:
        if view_mode == "Gallery":
            st.header("📸 Image Gallery")
            
            # Get images from database
            images = st.session_state.db.get_images(limit=gallery_limit)
            
            if images:
                # Display images in a grid
                cols = st.columns(2)
                
                for i, image in enumerate(images):
                    with cols[i % 2]:
                        try:
                            image_path = os.path.join(settings.IMAGES_DIR, image['filename'])
                            if os.path.exists(image_path):
                                # Display image
                                img = Image.open(image_path)
                                st.image(img, use_container_width=True)
                                
                                # Image info
                                with st.expander(f"📝 {image['prompt'][:50]}..."):
                                    st.markdown(f"**Prompt:** {image['prompt']}")
                                    st.markdown(f"**Style:** {image['expected_style'].title()}")
                                    st.markdown(f"**Created:** {image['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                                    
                                    if image.get('generation_time'):
                                        st.markdown(f"**Generation Time:** {image['generation_time']:.1f}s")
                                    
                                    if image.get('file_size'):
                                        st.markdown(f"**File Size:** {image['file_size']/1024:.1f} KB")
                                    
                                    # Download button
                                    if st.button(f"📥 Download", key=f"download_{image['id']}"):
                                        with open(image_path, "rb") as file:
                                            st.download_button(
                                                label="💾 Download Image",
                                                data=file.read(),
                                                file_name=f"{image['prompt'][:30]}.png",
                                                mime="image/png",
                                                key=f"download_btn_{image['id']}"
                                            )
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")
            else:
                st.info("🎨 No images generated yet. Create your first image!")
        
        elif view_mode == "Prompt History":
            st.header("📝 Prompt History")
            
            history = st.session_state.db.get_prompt_history()
            
            if history:
                for item in history:
                    with st.expander(f"📅 {item['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                        st.markdown(f"**Prompt:** {item['prompt']}")
                        st.markdown(f"**Style:** {item['expected_style'].title()}")
            else:
                st.info("📝 No prompt history available.")
        
        elif view_mode == "Statistics":
            st.header("📊 Statistics")
            
            if st.session_state.db.collection is not None:
                # Get all images for statistics
                all_images = st.session_state.db.get_images(limit=1000)
                
                if all_images:
                    # Style distribution
                    style_counts = {}
                    total_generation_time = 0
                    total_file_size = 0
                    
                    for img in all_images:
                        style = img['expected_style']
                        style_counts[style] = style_counts.get(style, 0) + 1
                        
                        if img.get('generation_time'):
                            total_generation_time += img['generation_time']
                        
                        if img.get('file_size'):
                            total_file_size += img['file_size']
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Images", len(all_images))
                    
                    with col2:
                        avg_time = total_generation_time / len(all_images) if all_images else 0
                        st.metric("Avg Generation Time", f"{avg_time:.1f}s")
                    
                    with col3:
                        avg_size = total_file_size / len(all_images) if all_images else 0
                        st.metric("Avg File Size", f"{avg_size/1024:.1f} KB")
                    
                    # Style distribution chart
                    st.subheader("🎨 Style Distribution")
                    st.bar_chart(style_counts)
                    
                    # Recent activity
                    st.subheader("📅 Recent Activity")
                    recent_images = all_images[:5]
                    for img in recent_images:
                        st.markdown(f"• **{img['created_at'].strftime('%Y-%m-%d %H:%M')}** - {img['prompt'][:50]}...")
                else:
                    st.info("📊 No data available for statistics.")
            else:
                st.error("❌ Database not connected.")

if st.session_state.view == "feedback":
    # get last image from the session state
    image_data = st.session_state.last_image
    image_stream = BytesIO(image_data)
    generation_time = st.session_state.generation_time

    st.title("📝 Feedback")
    st.write("Prompt:")
    st.markdown(f"> **{st.session_state.last_prompt}**")
    st.image(Image.open(image_stream), caption="Generated Image", width=512)

    rating = st.slider("How well does this image match your expectations? (1–10)", 1, 10, 5)
    comment = st.text_area("Optional comments")

    if st.button("Submit Feedback", use_container_width=False):
        # Save feedback
        feedback_data = FeedbackData(
            rating=rating,
            comment=comment
        )
        # # append to CSV
        # if os.path.exists("feedback.csv"):
        #     df = pd.read_csv("feedback.csv")
        #     df = pd.concat([df, pd.DataFrame([feedback_data])], ignore_index=True)
        # else:
        #     df = pd.DataFrame([feedback_data])
        # df.to_csv("feedback.csv", index=False)

        # Save image
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.png"
        filepath = os.path.join(settings.IMAGES_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Create record
        image_record = ImageRecord(
            id=image_id,
            prompt=st.session_state.last_prompt,
            expected_style=st.session_state.style,
            filename=filename,
            created_at=datetime.now(),
            generation_time=generation_time,
            status="completed",
            file_size=file_size,
            feedback_data=feedback_data
        )
        
        # Save to database
        st.session_state.db.save_image_record(image_record)
        
        # st.success(f"✅ Image generated successfully in {generation_time:.1f}s!")
        # st.balloons()

        st.success("✅ Feedback saved! Returning to main page...")
        # Switch back
        st.session_state.view = "main"
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.9em;">
    Made with ❤️ using Streamlit | Powered by Stable Diffusion & Hugging Face
</div>
""", unsafe_allow_html=True)