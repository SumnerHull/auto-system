class LidarVisualization {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
        this.scale = Math.min(this.width, this.height) / 2;
        
        // Set up the canvas
        this.ctx.translate(this.centerX, this.centerY);
        this.ctx.scale(1, -1);  // Flip Y axis to match Cartesian coordinates
        
        // Draw the initial grid
        this.drawGrid();
    }

    drawGrid() {
        this.ctx.save();
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 1;

        // Draw concentric circles
        for (let r = 0.2; r <= 1; r += 0.2) {
            this.ctx.beginPath();
            this.ctx.arc(0, 0, r * this.scale, 0, 2 * Math.PI);
            this.ctx.stroke();
        }

        // Draw radial lines
        for (let angle = 0; angle < 360; angle += 30) {
            const rad = angle * Math.PI / 180;
            this.ctx.beginPath();
            this.ctx.moveTo(0, 0);
            this.ctx.lineTo(
                Math.cos(rad) * this.scale,
                Math.sin(rad) * this.scale
            );
            this.ctx.stroke();
        }

        this.ctx.restore();
    }

    updateData(data) {
        // Clear the canvas
        this.ctx.clearRect(-this.centerX, -this.centerY, this.width, this.height);
        
        // Redraw the grid
        this.drawGrid();
        
        // Draw the LiDAR points
        this.ctx.save();
        this.ctx.fillStyle = '#ff0000';
        
        data.forEach(point => {
            const angle = point[1] * Math.PI / 180;  // Convert to radians
            const distance = point[2] / 1000;  // Convert mm to m and normalize
            
            const x = Math.cos(angle) * distance * this.scale;
            const y = Math.sin(angle) * distance * this.scale;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, 2 * Math.PI);
            this.ctx.fill();
        });
        
        this.ctx.restore();
    }
}

// Initialize the visualization when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const lidarViz = new LidarVisualization('lidarCanvas');
    
    // Update the visualization every second
    setInterval(() => {
        fetch('/api/lidar')
            .then(response => response.json())
            .then(data => {
                lidarViz.updateData(data);
            })
            .catch(error => console.error('Error fetching LiDAR data:', error));
    }, 1000);
}); 