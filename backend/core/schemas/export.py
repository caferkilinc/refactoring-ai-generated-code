"""Deterministically export the single model registry to JSON Schema and OpenAPI."""
import argparse
import copy
import json
from pathlib import Path

from . import models
from .field_docs import FIELD_DOCS

ROOT = Path(__file__).resolve().parents[3]
TOP_LEVEL = (models.SourceLocation, models.Symbol, models.DependencyEdge, models.Evidence, models.Finding,
             models.Metric, models.TestResult, models.Capability, models.LanguageAdapterCapabilities,
             models.IssueSelection, models.ContextPackage, models.PatchCandidate, models.ValidationResult,
             models.ContractBundle, models.ResultEnvelope, models.ErrorEnvelope, models.AdapterRequest, models.AdapterResult)


def schema_document():
    definitions = {}
    for model in TOP_LEVEL:
        schema = model.model_json_schema(ref_template='#/$defs/{model}')
        nested = schema.pop('$defs', {})
        for name, definition in nested.items():
            if name in definitions and definitions[name] != definition:
                raise ValueError('Conflicting shared schema: ' + name)
            definitions[name] = definition
        name = model.__name__
        if name in definitions and definitions[name] != schema:
            raise ValueError('Conflicting top-level schema: ' + name)
        definitions[name] = schema
    for definition in definitions.values():
        for name, prop in definition.get('properties', {}).items():
            if 'description' not in prop:
                prop['description'] = FIELD_DOCS[name]
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': models.SCHEMA_ID,
            '$ref': '#/$defs/ContractBundle', '$defs': definitions,
            '$comment': 'Structural constraints are necessary but not sufficient. Run validate_bundle for reference/safety invariants.'}


def api_document():
    definitions = schema_document()['$defs']

    def api_refs(value):
        if isinstance(value, dict):
            return {key: api_refs(item) for key, item in value.items()}
        if isinstance(value, list):
            return [api_refs(item) for item in value]
        return value.replace('#/$defs/', '#/components/schemas/') if isinstance(value, str) else value

    response = {'description': 'Versioned result; FIXTURE examples are synthetic, not deployed execution evidence.',
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ResultEnvelope'},
                                                 'examples': {'fixture': {'externalValue': 'examples/result.json'}}}}}
    error = {'description': 'Static safe error with stable code, origin and retryability.',
             'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorEnvelope'},
                                              'examples': {'stale': {'externalValue': 'examples/error.json'}}}}}

    def operation(identifier, parameter=None, request=None):
        value = {'operationId': identifier, 'x-implementation-status': 'CONTRACT_DEFINED',
                 'description': 'Design contract only. No running HTTP service is delivered by F02-CONTRACT.',
                 'responses': {'200': copy.deepcopy(response), '400': copy.deepcopy(error),
                               '409': copy.deepcopy(error), '422': copy.deepcopy(error), '503': copy.deepcopy(error)}}
        if parameter:
            value['parameters'] = [{'name': parameter, 'in': 'path', 'required': True,
                                    'schema': {'type': 'string', 'pattern': '^' + parameter.removesuffix('_id')
                                               + ':[A-Za-z0-9][A-Za-z0-9._-]{0,127}$'}}]
        if request:
            content = {'schema': {'$ref': '#/components/schemas/' + request}}
            if request == 'IssueSelection':
                content['examples'] = {'fixture': {'externalValue': 'examples/issue-selection.json'}}
            value['requestBody'] = {'required': True, 'content': {'application/json': content}}
        return value

    return {'openapi': '3.1.1', 'jsonSchemaDialect': 'https://json-schema.org/draft/2020-12/schema',
            'info': {'title': 'Genesis CIR/API contract', 'version': models.VERSION,
                     'description': 'CONTRACT_DEFINED. Runtime endpoints, authorization services and storage are future work.'},
            'x-implementation-status': 'CONTRACT_DEFINED',
            'paths': {
                '/api/analyses/{analysis_id}/findings': {'get': operation('listFindings', 'analysis_id')},
                '/api/analyses/{analysis_id}/issue-selections': {'post': operation('selectIssues', 'analysis_id', 'IssueSelection')},
                '/api/versions/{version_id}/capabilities': {'get': operation('getCapabilities', 'version_id')},
                '/api/patches/{patch_id}/diff': {'get': operation('getPatchDiffMetadata', 'patch_id')},
            },
            'components': {'schemas': api_refs(definitions)}}


def generated_files():
    def encode(value):
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    return {ROOT / 'backend/core/schemas/cir-1.0.0.schema.json': encode(schema_document()),
            ROOT / 'docs/contracts/openapi-1.0.0.json': encode(api_document()),
            ROOT / 'docs/contracts/DATA-DICTIONARY.md': data_dictionary()}


def data_dictionary():
    schema = schema_document()

    def type_text(prop):
        if '$ref' in prop:
            return prop['$ref'].split('/')[-1]
        if 'anyOf' in prop:
            return ' or '.join(type_text(item) for item in prop['anyOf'])
        if prop.get('type') == 'array':
            return 'array of ' + type_text(prop.get('items', {}))
        if 'oneOf' in prop:
            return 'one of ' + ', '.join(type_text(item) for item in prop['oneOf'])
        return prop.get('type', 'object')

    lines = ['# CIR 1.0.0 data dictionary', '',
             'Generated from the authoritative Pydantic registry and shared field descriptions.',
             'Every wire field is required in v1. A nullable field is supplied explicitly as null;',
             'null does not mean zero, false, empty, unsupported or successful.',
             'Identifiers below are logical schema IDs, not deployed download URLs.', '',
             'Cross-record and state-dependent constraints are defined in [SEMANTICS.md](SEMANTICS.md).', '']
    for name, definition in sorted(schema['$defs'].items()):
        lines += ['## ' + name, '', definition.get('description', name), '',
                  '`' + models.SCHEMA_ID + '#/$defs/' + name + '`', '',
                  '| Field | Type | Required | Values / constraints | Meaning |',
                  '|---|---|---|---|---|']
        for field, prop in definition.get('properties', {}).items():
            constraints = {key: prop[key] for key in ('const', 'enum', 'pattern', 'minimum', 'maximum',
                           'minLength', 'maxLength', 'minItems', 'maxItems') if key in prop}
            describe = prop.get('description', '').replace('|', '\\|').replace('\n', ' ')
            lines.append('| `' + field + '` | ' + type_text(prop).replace('|', '\\|') + ' | '
                         + ('yes' if field in definition.get('required', []) else 'no') + ' | '
                         + json.dumps(constraints, ensure_ascii=False).replace('|', '\\|') + ' | ' + describe + ' |')
        lines.append('')
    return '\n'.join(lines).rstrip('\n') + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if any committed export is missing or stale.')
    args = parser.parse_args()
    for path, content in generated_files().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                raise SystemExit('Missing or stale generated contract: ' + str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
    print('Contract exports are current' if args.check else 'Contract exports written')


if __name__ == '__main__':
    main()
