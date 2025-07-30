"""tests/test_exceptions.py"""

import unittest

from src.obs_layer_data_process.processors.stratus.utils.exceptions import (
    StratusProcessorError, MessageLengthError, InvalidEventDataError,
    NoS3FileLoadedError, NoVariablesConfiguredError, NoCampaignsFoundError,
    UnsupportedMessageTypeError
)
from src.obs_layer_data_process.processors.mbaas.utils.exceptions import (
    MbaasProcessorError, AppConsumerNotFoundError, ServiceNotFoundError,
    NoMinimumDataError, NoVariablesConfiguredError as MbaasNoVariablesConfiguredError,
    VariableExtractionError, InvalidEventDataError as MbaasInvalidEventDataError
)
from src.obs_layer_data_process.processors.workflow.utils.exceptions import (
    MbaasWorkflowProcessorError, AppConsumerNotFoundError as WorkflowAppConsumerNotFoundError,
    ServiceNotFoundError as WorkflowServiceNotFoundError, 
    NoMinimumDataError as WorkflowNoMinimumDataError,
    NoVariablesConfiguredError as WorkflowNoVariablesConfiguredError,
    VariableExtractionError as WorkflowVariableExtractionError,
    InvalidEventDataError as WorkflowInvalidEventDataError,
    NoTransactionDataFound
)


class TestStratusExceptions(unittest.TestCase):
    
    def test_stratus_processor_error(self):
        error = StratusProcessorError("Test error", {"key": "value"})
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, {"key": "value"})
    
    def test_message_length_error(self):
        error = MessageLengthError("test_message")
        self.assertTrue("longitud requerida" in str(error))
    
    def test_invalid_event_data_error(self):
        error = InvalidEventDataError("Missing field")
        self.assertTrue("Missing field" in str(error))
    
    def test_other_exceptions(self):
        self.assertTrue(issubclass(NoS3FileLoadedError, StratusProcessorError))
        self.assertTrue(issubclass(NoVariablesConfiguredError, StratusProcessorError))
        self.assertTrue(issubclass(NoCampaignsFoundError, StratusProcessorError))
        self.assertTrue(issubclass(UnsupportedMessageTypeError, StratusProcessorError))

class TestMbaasExceptions(unittest.TestCase):
    
    def test_mbaas_processor_error(self):
        error = MbaasProcessorError("Test error", {"key": "value"})
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, {"key": "value"})
    
    def test_app_consumer_not_found_error(self):
        error = AppConsumerNotFoundError("app1", "session1")
        self.assertTrue("app1" in str(error))
        self.assertTrue("session1" in str(error))
    
    def test_service_not_found_error(self):
        error = ServiceNotFoundError("service1", "app1", "session1")
        self.assertTrue("service1" in str(error))
        self.assertTrue("app1" in str(error))
    
    def test_no_minimum_data_error(self):
        error = NoMinimumDataError(["app1"], "app1", "service1", "session1")
        self.assertTrue("no tiene un valor válido" in str(error))
    
    def test_other_exceptions(self):
        self.assertTrue(issubclass(MbaasNoVariablesConfiguredError, MbaasProcessorError))
        self.assertTrue(issubclass(VariableExtractionError, MbaasProcessorError))
        self.assertTrue(issubclass(MbaasInvalidEventDataError, MbaasProcessorError))

class TestWorkflowExceptions(unittest.TestCase):
    
    def test_workflow_processor_error(self):
        error = MbaasWorkflowProcessorError("Test error", {"key": "value"})
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, {"key": "value"})
    
    def test_app_consumer_not_found_error(self):
        error = WorkflowAppConsumerNotFoundError("app1")
        self.assertTrue("app1" in str(error))
    
    def test_service_not_found_error(self):
        error = WorkflowServiceNotFoundError("service1", "app1")
        self.assertTrue("service1" in str(error))
        self.assertTrue("app1" in str(error))
    
    def test_no_minimum_data_error(self):
        error = WorkflowNoMinimumDataError(["app1"], "app1", "service1", "session1", "entity1")
        self.assertTrue("no tiene un valor válido" in str(error))
    
    def test_no_transaction_data_found(self):
        error = NoTransactionDataFound("missing fields")
        self.assertTrue("transactionData" in str(error))
    
    def test_other_exceptions(self):
        self.assertTrue(issubclass(WorkflowNoVariablesConfiguredError, MbaasWorkflowProcessorError))
        self.assertTrue(issubclass(WorkflowVariableExtractionError, MbaasWorkflowProcessorError))
        self.assertTrue(issubclass(WorkflowInvalidEventDataError, MbaasWorkflowProcessorError))
