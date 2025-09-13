import unittest
import tempfile
import os
import shutil
import yaml
from unittest.mock import patch, mock_open
from src.config_validator import (
    ConfigValidator,
    ConfigValidationError,
    validate_directories,
    validate_image_files
)


class TestConfigValidator(unittest.TestCase):
    """Test cases for ConfigValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_basic_iiif_settings_valid(self):
        """Test validation of valid basic IIIF settings."""
        config = {
            'iiif_base_url': 'https://example.com/iiif/2',
            'tile_size': 512,
            'base_quality': 80
        }
        # Should not raise an exception
        self.validator._validate_basic_settings(config)
    
    def test_validate_basic_iiif_settings_missing_url(self):
        """Test validation fails when iiif_base_url is missing."""
        config = {
            'tile_size': 512,
            'base_quality': 80
        }
        self.validator._validate_basic_settings(config)
        self.assertTrue(any('iiif_base_url' in error for error in self.validator.errors))
    
    def test_validate_basic_iiif_settings_invalid_tile_size(self):
        """Test validation fails with invalid tile size."""
        config = {
            'iiif_base_url': 'https://example.com/iiif/2',
            'tile_size': 0,
            'base_quality': 80
        }
        self.validator._validate_basic_settings(config)
        self.assertTrue(any('tile_size' in error for error in self.validator.errors))
    
    def test_validate_basic_iiif_settings_invalid_quality(self):
        """Test validation fails with invalid quality."""
        config = {
            'iiif_base_url': 'https://example.com/iiif/2',
            'tile_size': 512,
            'base_quality': 150
        }
        self.validator._validate_basic_settings(config)
        self.assertTrue(any('base_quality' in error for error in self.validator.errors))
    
    def test_validate_tiling_config_valid(self):
        """Test validation of valid tiling configuration."""
        tiling_config = {
            'formats': ['jpg', 'webp'],
            'qualities': [50, 80, 95],
            'sizes': [256, 512, 1024]
        }
        # Should not raise an exception
        self.validator._validate_tiling_config(tiling_config)
    
    def test_validate_tiling_config_invalid_format(self):
        """Test validation fails with invalid format."""
        tiling_config = {
            'formats': ['jpg', 'invalid_format'],
            'qualities': [50, 80, 95],
            'sizes': [256, 512, 1024]
        }
        self.validator._validate_tiling_config(tiling_config)
        self.assertTrue(any('invalid_format' in error for error in self.validator.errors))
    
    def test_validate_tiling_config_invalid_quality_range(self):
        """Test validation fails with quality out of range."""
        tiling_config = {
            'formats': ['jpg', 'webp'],
            'qualities': [0, 80, 150],
            'sizes': [256, 512, 1024]
        }
        self.validator._validate_tiling_config(tiling_config)
        self.assertTrue(any('quality' in error for error in self.validator.errors))
    
    def test_validate_enable_config_valid(self):
        """Test validation of valid enable configuration."""
        enable_config = {
            'regions': True,
            'size_variants': False,
            'rotations': True,
            'tiles': True
        }
        # Should not raise an exception
        self.validator._validate_enable_config(enable_config)
    
    def test_validate_enable_config_invalid_type(self):
        """Test validation fails with non-boolean values."""
        enable_config = {
            'regions': 'yes',  # Should be boolean
            'size_variants': False,
            'rotations': True,
            'tiles': True
        }
        self.validator._validate_enable_config(enable_config)
        self.assertTrue(any('boolean' in error for error in self.validator.errors))


class TestValidateDirectories(unittest.TestCase):
    """Test cases for validate_directories function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.masters_dir = os.path.join(self.temp_dir, 'masters')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.masters_dir)
        os.makedirs(self.output_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_directories_success(self):
        """Test successful directory validation."""
        config = {
            'masters_dir': self.masters_dir,
            'output_dir': self.output_dir
        }
        # Should not raise an exception
        validate_directories(config)
    
    def test_validate_directories_missing_masters(self):
        """Test validation fails when masters directory doesn't exist."""
        config = {
            'masters_dir': '/nonexistent/path',
            'output_dir': self.output_dir
        }
        with self.assertRaises(ConfigValidationError) as cm:
            validate_directories(config)
        self.assertIn('masters_dir', str(cm.exception))


class TestValidateImageFiles(unittest.TestCase):
    """Test cases for validate_image_files function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_image_files_with_valid_files(self):
        """Test validation with valid image files."""
        # Create mock image files
        image_files = ['test1.jpg', 'test2.png', 'test3.webp']
        for filename in image_files:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write('mock image content')
        
        result = validate_image_files(self.temp_dir)
        self.assertEqual(len(result), 3)
        for filepath in result:
            self.assertTrue(os.path.exists(filepath))
    
    def test_validate_image_files_no_images(self):
        """Test validation when no image files exist."""
        # Create non-image files
        with open(os.path.join(self.temp_dir, 'readme.txt'), 'w') as f:
            f.write('not an image')
        
        with self.assertRaises(ConfigValidationError) as cm:
            validate_image_files(self.temp_dir)
        self.assertIn('No valid image files', str(cm.exception))
    
    def test_validate_image_files_nonexistent_directory(self):
        """Test validation fails with nonexistent directory."""
        with self.assertRaises(ConfigValidationError) as cm:
            validate_image_files('/nonexistent/path')
        self.assertIn('does not exist', str(cm.exception))


if __name__ == '__main__':
    unittest.main()