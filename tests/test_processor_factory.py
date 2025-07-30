"""tests/test_processor_factory.py"""

import unittest

from unittest.mock import MagicMock, patch

from src.obs_layer_data_process.core.factory.processor_factory import MessageProcessorFactory
from src.obs_layer_data_process.processors.mbaas.processor import MbaasProcessor
from src.obs_layer_data_process.processors.stratus.processor import StratusProcessor
from src.obs_layer_data_process.processors.stratus.scalabe_processor import ScalableStratusProcessor
from src.obs_layer_data_process.processors.workflow.processor import WorkflowProcessor


class TestProcessorFactory(unittest.TestCase):
    
    def setUp(self):
        self.factory = MessageProcessorFactory()
        
    def test_create_mbaas_processor(self):
        s3_config = {"test": "config"}
        processor = self.factory.create_processor("mbaas", s3_config=s3_config)
        self.assertIsInstance(processor, MbaasProcessor)
        
    def test_create_stratus_processor(self):
        s3_config = {"test": "config"}
        processor = self.factory.create_processor("stratus", s3_config=s3_config)
        self.assertIsInstance(processor, StratusProcessor)
        
    def test_create_scalable_stratus_processor(self):
        s3_config = {"test": "config"}
        processor = self.factory.create_processor("scalable_stratus", s3_config=s3_config)
        self.assertIsInstance(processor, ScalableStratusProcessor)
        
    def test_create_workflow_processor(self):
        s3_config = {"test": "config"}
        processor = self.factory.create_processor("workflow", s3_config=s3_config)
        self.assertIsInstance(processor, WorkflowProcessor)
        
    def test_case_insensitive_processor_type(self):
        s3_config = {"test": "config"}
        processor = self.factory.create_processor("MBAAS", s3_config=s3_config)
        self.assertIsInstance(processor, MbaasProcessor)
        
    def test_unsupported_processor_type(self):
        with self.assertRaises(ValueError) as context:
            self.factory.create_processor("unsupported_type")
        self.assertTrue("Unsupported processor type" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
