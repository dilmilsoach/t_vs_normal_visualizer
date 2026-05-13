from flask import Flask, render_template, request
import numpy as np
from scipy.stats import norm, t
import matplotlib
# Forces Matplotlib to run without a GUI window (critical for headless web servers like Render)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    sample_size = 5
    
    if request.method == "POST":
        try:
            sample_size = int(request.form.get("sample_size", 5))
            if sample_size < 2: sample_size = 2
            if sample_size > 500: sample_size = 500
        except ValueError:
            sample_size = 5

    df = sample_size - 1
    x = np.linspace(-4, 4, 1000)

    # Calculate probability density function evaluations
    normal_pdf = norm.pdf(x, 0, 1)
    t_pdf = t.pdf(x, df)

    # Initialize Matplotlib Figure
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    
    # Render traces
    ax.plot(x, normal_pdf, color='#ef4444', lw=2.5, label='Standard Normal Distribution')
    ax.plot(x, t_pdf, color='#3b82f6', lw=2.5, linestyle='--', label=f"Student's t-Distribution (df={df})")
    
    # Styling and Grid layout
    ax.set_title(f"Normal vs Student's t-Distribution (n = {sample_size})", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Standard Deviations (x)", fontsize=10)
    ax.set_ylabel("Probability Density", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#e2e8f0')
    
    # Remove top and right borders for a cleaner, modern interface
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    # Extract structural layout padding margins
    plt.tight_layout()

    # Save visualization directly to binary memory buffer stream
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    # Convert binary buffer into a Base64 string safe for HTML injection
    plot_url = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Liberate server memory blocks allocated to graph instances

    return render_template("index.html", plot_url=plot_url, sample_size=sample_size)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
