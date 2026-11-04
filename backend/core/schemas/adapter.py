"""LanguageAdapter interface only. No adapter or external tool is implemented here."""
from typing import Protocol

from .models import (AdapterRequest, AdapterResult, Capability, ContractBundle,
                     LanguageAdapterCapabilities, Scope)
from .validation import ContractViolation, check, validate_bundle


class LanguageAdapter(Protocol):
    def describe(self, scope: Scope, language: str, component_id: str) -> LanguageAdapterCapabilities:
        """Declare each capability independently using real evidence or explicit unavailability."""
        ...

    def execute(self, request: AdapterRequest) -> AdapterResult:
        """Future implementation must call the capability guard before tool execution."""
        ...


def require_capability(request: AdapterRequest, bundle: ContractBundle, *, patch_policy=None) -> Capability:
    """Pure contract precondition; does not launch a tool, worker or provider."""
    bundle = validate_bundle(bundle, patch_policy=patch_policy)
    check(bundle.mode == 'INTERCHANGE', 'UNAVAILABLE_CAPABILITY', 'mode')
    records = {record.id: record for record in bundle.records}
    declaration = records.get(request.adapter_capabilities_id)
    capability = records.get(request.capability_id)
    check(request.scope == bundle.scope, 'SCOPE_MISMATCH', 'scope')
    if not (isinstance(declaration, LanguageAdapterCapabilities) and isinstance(capability, Capability)
            and declaration.implementation_state == 'RUNTIME_IMPLEMENTED'
            and request.capability_id in declaration.capability_ids
            and request.language == declaration.language == capability.language
            and request.component_id == declaration.component_id == capability.component_id
            and request.operation == capability.capability and capability.status == 'SUPPORTED'):
        raise ContractViolation('UNAVAILABLE_CAPABILITY', 'capability_id')
    check(any(artifact.id == request.input_artifact_id for artifact in bundle.artifacts),
          'BROKEN_REFERENCE', 'input_artifact_id')
    return capability
