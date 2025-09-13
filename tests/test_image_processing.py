import unittest
import tempfile
import os
import shutil
import json
from PIL import Image
from unittest.mock import patch, MagicMock
from src.config_loader import load_config
from src.tile_level0 import process_image as process_image_level0
from src.tile_level2_static import process_image_static
from src.tile_level2_comprehensive import process_image_comprehensive


class TestImageProcessing(unittest.TestCase):
    """Test cases for image processing functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, 'test_image.jpg')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a test image
        test_image = Image.new('RGB', (1024, 768), color='red')
        test_image.save(self.test_image_path, 'JPEG')
        
        # Mock configuration
        self.mock_config = {
            'iiif_base_url': 'https://example.com/iiif/2',
            'tile_size': 512,
            'base_quality': 80,
            'tiling': {
                'formats': ['jpg', 'webp'],
                'qualities': [50, 80, 95],
                'sizes': [256, 512, 1024]
            },
            'enable': {
                'regions': True,
                'size_variants': True,
                'rotations': False,
                'tiles': True
            }
        }
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_process_image_level0_creates_tiles(self):
        """Test that level 0 processing creates tile directories."""
        process_image_level0(self.test_image_path, self.output_dir, self.mock_config)
        
        # Check that output directory structure is created
        image_id = os.path.splitext(os.path.basename(self.test_image_path))[0]
        image_output_dir = os.path.join(self.output_dir, image_id)
        
        self.assertTrue(os.path.exists(image_output_dir))
        
        # Check for info.json
        info_path = os.path.join(image_output_dir, 'info.json')
        self.assertTrue(os.path.exists(info_path))
        
        # Validate info.json content
        with open(info_path, 'r') as f:
            info = json.load(f)
            self.assertIn('@context', info)
            self.assertIn('width', info)
            self.assertIn('height', info)
            self.assertEqual(info['width'], 1024)
            self.assertEqual(info['height'], 768)
    
    def test_process_image_static_creates_variants(self):
        """Test that static processing creates size variants."""
        process_image_static(self.test_image_path, self.output_dir, self.mock_config)
        
        # Check that output directory structure is created
        image_id = os.path.splitext(os.path.basename(self.test_image_path))[0]
        image_output_dir = os.path.join(self.output_dir, image_id)
        
        self.assertTrue(os.path.exists(image_output_dir))
        
        # Check for info.json
        info_path = os.path.join(image_output_dir, 'info.json')
        self.assertTrue(os.path.exists(info_path))
    
    def test_process_image_comprehensive_creates_full_structure(self):
        """Test that comprehensive processing creates full IIIF structure."""
        process_image_comprehensive(self.test_image_path, self.output_dir, self.mock_config)
        
        # Check that output directory structure is created
        image_id = os.path.splitext(os.path.basename(self.test_image_path))[0]
        image_output_dir = os.path.join(self.output_dir, image_id)
        
        self.assertTrue(os.path.exists(image_output_dir))
        
        # Check for info.json
        info_path = os.path.join(image_output_dir, 'info.json')
        self.assertTrue(os.path.exists(info_path))
        
        # Validate info.json content includes comprehensive features
        with open(info_path, 'r') as f:
            info = json.load(f)
            self.assertIn('profile', info)
            if self.mock_config['enable']['regions']:
                self.assertIn('supports', info['profile'][1])
    
    def test_info_json_reflects_configuration(self):
        """Test that info.json reflects the current configuration."""
        # Test with regions disabled
        config_no_regions = self.mock_config.copy()
        config_no_regions['enable']['regions'] = False
        
        process_image_comprehensive(self.test_image_path, self.output_dir, config_no_regions)
        
        image_id = os.path.splitext(os.path.basename(self.test_image_path))[0]
        info_path = os.path.join(self.output_dir, image_id, 'info.json')
        
        with open(info_path, 'r') as f:
            info = json.load(f)
            # Should not include region support when disabled
            if 'profile' in info and len(info['profile']) > 1:
                supports = info['profile'][1].get('supports', [])
                self.assertNotIn('regionByPx', supports)
    
    def test_image_processing_with_different_formats(self):
        """Test image processing with different input formats."""
        # Test with PNG
        png_path = os.path.join(self.temp_dir, 'test_image.png')
        test_image = Image.new('RGBA', (512, 512), color=(255, 0, 0, 128))
        test_image.save(png_path, 'PNG')
        
        process_image_level0(png_path, self.output_dir, self.mock_config)
        
        image_id = os.path.splitext(os.path.basename(png_path))[0]
        image_output_dir = os.path.join(self.output_dir, image_id)
        
        self.assertTrue(os.path.exists(image_output_dir))
        
        # Check for info.json
        info_path = os.path.join(image_output_dir, 'info.json')
        self.assertTrue(os.path.exists(info_path))
    
    def test_error_handling_invalid_image(self):
        """Test error handling with invalid image file."""
        # Create a non-image file
        invalid_path = os.path.join(self.temp_dir, 'not_an_image.txt')
        with open(invalid_path, 'w') as f:
            f.write('This is not an image')
        
        # Should handle the error gracefully
        with self.assertRaises(Exception):
            process_image_level0(invalid_path, self.output_dir, self.mock_config)
    
    def test_configuration_parameter_usage(self):
        """Test that configuration parameters are properly used."""
        # Test with custom tile size
        custom_config = self.mock_config.copy()
        custom_config['tile_size'] = 256
        
        process_image_level0(self.test_image_path, self.output_dir, custom_config)
        
        image_id = os.path.splitext(os.path.basename(self.test_image_path))[0]
        info_path = os.path.join(self.output_dir, image_id, 'info.json')
        
        with open(info_path, 'r') as f:
            info = json.load(f)
            # Check that tile size is reflected in info.json
            if 'tiles' in info:
                self.assertEqual(info['tiles'][0]['width'], 256)
                self.assertEqual(info['tiles'][0]['height'], 256)


class TestImageProcessingIntegration(unittest.TestCase):
    """Integration tests for image processing pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.masters_dir = os.path.join(self.temp_dir, 'masters')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.masters_dir)
        os.makedirs(self.output_dir)
        
        # Create multiple test images
        for i, (width, height) in enumerate([(1024, 768), (512, 512), (2048, 1536)]):
            image_path = os.path.join(self.masters_dir, f'test_image_{i+1}.jpg')
            test_image = Image.new('RGB', (width, height), color=['red', 'green', 'blue'][i])
            test_image.save(image_path, 'JPEG')
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.config_loader.load_config')
    def test_full_processing_pipeline(self, mock_load_config):
        """Test the full processing pipeline with multiple images."""
        mock_config = {
            'iiif_base_url': 'https://example.com/iiif/2',
            'tile_size': 512,
            'base_quality': 80,
            'tiling': {
                'formats': ['jpg'],
                'qualities': [80],
                'sizes': [512]
            },
            'enable': {
                'regions': True,
                'size_variants': False,
                'rotations': False,
                'tiles': True
            }
        }
        mock_load_config.return_value = mock_config
        
        # Process all images
        for filename in os.listdir(self.masters_dir):
            if filename.endswith('.jpg'):
                image_path = os.path.join(self.masters_dir, filename)
                process_image_level0(image_path, self.output_dir, mock_config)
        
        # Verify all images were processed
        processed_images = os.listdir(self.output_dir)
        self.assertEqual(len(processed_images), 3)
        
        # Verify each image has proper structure
        for image_dir in processed_images:
            image_output_path = os.path.join(self.output_dir, image_dir)
            self.assertTrue(os.path.isdir(image_output_path))
            
            info_path = os.path.join(image_output_path, 'info.json')
            self.assertTrue(os.path.exists(info_path))
            
            # Validate info.json structure
            with open(info_path, 'r') as f:
                info = json.load(f)
                required_fields = ['@context', '@id', 'protocol', 'width', 'height', 'profile']
                for field in required_fields:
                    self.assertIn(field, info)


if __name__ == '__main__':
    unittest.main()