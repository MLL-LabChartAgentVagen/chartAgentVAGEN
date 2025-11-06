"""
Binary mask generation with X and Y axes included
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from utils.logger import logger
import cv2

class ImageDiffMask:
    def __init__(self, chart_id):
        """Initialize the ImageDiffMask class."""
        self.mask = None
        self.img1 = None
        self.img2 = None
        self.params = None
        self._init_params(chart_id)

    def _init_params(self, chart_id: str):\
        # Large self.params[0], lower the X mask bottom
        # Large self.params[1], righter the Y mask right edge
        if chart_id == '1_bar_img_1':
            self.params = [0.19, 200]  # X axis mask param, Y axis mask param
        elif chart_id == '1_bar_img_2':
            self.params = [0.32, 260]  # X axis mask param, Y axis mask param
        
    def load_images(self, img1_path, img2_path):
        """
        Load two images and ensure they have the same size.
        
        Args:
            img1_path (str): Path to the first image
            img2_path (str): Path to the second image
            
        Returns:
            bool: True if images are loaded successfully, False otherwise
        """
        try:
            self.img1 = np.array(Image.open(img1_path).convert('RGB'))
            self.img2 = np.array(Image.open(img2_path).convert('RGB'))
            
            if self.img1.shape != self.img2.shape:
                logger.error("Error: Images must have the same dimensions")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading images: {e}")
            return False
    
    def generate_mask(self, threshold=20, include_axes=True):
        """
        Generate binary mask based on pixel differences between the two images.
        Also include X and Y axes in the mask using simplified approach.
        
        Args:
            threshold (int): Threshold for color difference (default: 20)
            include_axes (bool): Whether to include X and Y axes in the mask (default: True)
            
        Returns:
            numpy.ndarray: Binary mask where 1 indicates different regions and axes
        """
        if self.img1 is None or self.img2 is None:
            logger.error("Error: Images not loaded")
            return None
            
        # Calculate per-channel differences
        diff_r = np.abs(self.img1[:,:,0].astype(float) - self.img2[:,:,0].astype(float))
        diff_g = np.abs(self.img1[:,:,1].astype(float) - self.img2[:,:,1].astype(float))
        diff_b = np.abs(self.img1[:,:,2].astype(float) - self.img2[:,:,2].astype(float))
        
        # Combine channel differences
        diff_combined = np.maximum.reduce([diff_r, diff_g, diff_b])
        
        # Create binary mask based on threshold
        diff_mask = (diff_combined > threshold).astype(np.uint8)
        
        # Initialize full mask with the difference mask
        self.mask = diff_mask.copy()
        
        # Add X and Y axes to the mask if requested
        if include_axes:
            height, width = self.img1.shape[:2]
            
            # Create a grayscale version of the image for analysis
            gray = cv2.cvtColor(self.img1, cv2.COLOR_RGB2GRAY)
            
            # Find the bounding box of the changing bar (from diff_mask)
            y_indices, x_indices = np.where(diff_mask > 0)
            if len(y_indices) > 0 and len(x_indices) > 0:
                bar_top = np.min(y_indices)
                bar_bottom = np.max(y_indices)
                bar_left = np.min(x_indices)
                bar_right = np.max(x_indices)
            else:
                # If no difference is detected, use default values
                bar_top, bar_bottom = int(height * 0.4), int(height * 0.8)
                bar_left, bar_right = int(width * 0.2), int(width * 0.3)
            
            # Create a separate mask for the axes
            axes_mask = np.zeros_like(diff_mask)
            
            # --------- X-axis mask ---------
            # Find where the x-axis is likely to be (usually at the bottom of the bars)
            # Add a fixed amount for the x-axis thickness
            x_axis_top = bar_bottom  # Start right from the bottom of the bar (bar_bottom + k, k below bar bottom || bar_bottom - k, k above bar bottom)
            # Extend to the bottom with enough margin for ticks and labels
            x_axis_height = int(height * self.params[0])  # Make this 19% of image height
            x_axis_bottom = min(height, x_axis_top + x_axis_height)
            
            # Mask the entire X-axis region 
            axes_mask[x_axis_top:x_axis_bottom, :] = 1
            
            # --------- Y-axis mask ---------
            # Find where the y-axis is likely to be (usually to the left of the bars)
            # Make sure to leave enough space between the y-axis mask and the bar
            # y_axis_right = max(int(width * 0.06), bar_left - 100)  # Stop well before the leftmost bar
            y_axis_right = self.params[1]
            
            # Mask the entire Y-axis region including labels
            axes_mask[:, 0:y_axis_right] = 1
            
            # Combine the masks
            self.mask = np.logical_or(diff_mask, axes_mask).astype(np.uint8)
        
        return self.mask
    
    def save_mask(self, output_path):
        """
        Save the binary mask as an image.
        
        Args:
            output_path (str): Path where to save the mask
        """
        if self.mask is None:
            logger.error("Error: Mask not generated yet")
            return
            
        mask_img = Image.fromarray(self.mask * 255)  # Convert to 0-255 range
        mask_img.save(output_path)
    
    def visualize_results(self, save_path=None):
        """
        Display or save a figure with three subplots: both input images and the mask.
        
        Args:
            save_path (str, optional): Path to save the visualization
        """
        if any(x is None for x in [self.img1, self.img2, self.mask]):
            logger.error("Error: Images or mask not available")
            return
            
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        
        # Display first image
        ax1.imshow(self.img1)
        ax1.set_title('(A) Original Image')
        ax1.axis('off')
        
        # Display second image
        ax2.imshow(self.img2)
        ax2.set_title('(B) Masked Image (Gray Mask)')
        ax2.axis('off')
        
        # Display mask with inverted colors in visualization
        ax3.imshow(1 - self.mask, cmap='binary', vmin=0, vmax=1)
        ax3.set_title('(C) Binary Mask')
        ax3.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        else:
            plt.show()
        
        plt.close()
        

def bar_mask_generation(args, root_path: str, chart_id: str, mask_id: str, threshold: int=10):
    # Initialize the class
    diff_mask = ImageDiffMask(chart_id)
    
    # Load images
    success = diff_mask.load_images(f"{root_path}/{chart_id}.png", f"{root_path}/{mask_id.replace('mask', 'maskcolor')}.png")
    
    if success:
        # Generate the mask with axes included
        mask = diff_mask.generate_mask(threshold=threshold, include_axes=True)
        
        # Subtask 2: 2_mask
        if '2' in args.construction_subtask:
            diff_mask.save_mask(f"{root_path}/{mask_id}.png")
            logger.info(f"Mask saved to `{root_path}/{mask_id}.png`")
        
        # Subtask 3: 3_combined
        if '3' in args.construction_subtask:
            diff_mask.visualize_results(f"{root_path}/{mask_id}_all.png")
            logger.info(f"Comparison plot saved to `{root_path}/{mask_id}_all.png`")