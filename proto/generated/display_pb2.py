# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: display.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='display.proto',
  package='display',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rdisplay.proto\x12\x07\x64isplay\"\x85\x01\n\rLaunchRequest\x12#\n\x1b\x43ontrolSignalEndpoint_STAGE\x18\x01 \x01(\t\x12!\n\x19\x43odeMappingEndpoint_STAGE\x18\x02 \x01(\t\x12\x17\n\x0fSignalingServer\x18\x03 \x01(\t\x12\x13\n\x0bprocessName\x18\x04 \x01(\t\"?\n\x10TerminateRequest\x12\x13\n\x0bprocessName\x18\x01 \x01(\t\x12\x16\n\x0esubProcessName\x18\x02 \x01(\t\"(\n\x05Reply\x12\x0e\n\x06result\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t2u\n\x06Launch\x12\x31\n\x05Start\x12\x16.display.LaunchRequest\x1a\x0e.display.Reply\"\x00\x12\x38\n\tTerminate\x12\x19.display.TerminateRequest\x1a\x0e.display.Reply\"\x00\x62\x06proto3'
)




_LAUNCHREQUEST = _descriptor.Descriptor(
  name='LaunchRequest',
  full_name='display.LaunchRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ControlSignalEndpoint_STAGE', full_name='display.LaunchRequest.ControlSignalEndpoint_STAGE', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='CodeMappingEndpoint_STAGE', full_name='display.LaunchRequest.CodeMappingEndpoint_STAGE', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='SignalingServer', full_name='display.LaunchRequest.SignalingServer', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='processName', full_name='display.LaunchRequest.processName', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=160,
)


_TERMINATEREQUEST = _descriptor.Descriptor(
  name='TerminateRequest',
  full_name='display.TerminateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='processName', full_name='display.TerminateRequest.processName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='subProcessName', full_name='display.TerminateRequest.subProcessName', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=162,
  serialized_end=225,
)


_REPLY = _descriptor.Descriptor(
  name='Reply',
  full_name='display.Reply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='display.Reply.result', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message', full_name='display.Reply.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=227,
  serialized_end=267,
)

DESCRIPTOR.message_types_by_name['LaunchRequest'] = _LAUNCHREQUEST
DESCRIPTOR.message_types_by_name['TerminateRequest'] = _TERMINATEREQUEST
DESCRIPTOR.message_types_by_name['Reply'] = _REPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LaunchRequest = _reflection.GeneratedProtocolMessageType('LaunchRequest', (_message.Message,), {
  'DESCRIPTOR' : _LAUNCHREQUEST,
  '__module__' : 'display_pb2'
  # @@protoc_insertion_point(class_scope:display.LaunchRequest)
  })
_sym_db.RegisterMessage(LaunchRequest)

TerminateRequest = _reflection.GeneratedProtocolMessageType('TerminateRequest', (_message.Message,), {
  'DESCRIPTOR' : _TERMINATEREQUEST,
  '__module__' : 'display_pb2'
  # @@protoc_insertion_point(class_scope:display.TerminateRequest)
  })
_sym_db.RegisterMessage(TerminateRequest)

Reply = _reflection.GeneratedProtocolMessageType('Reply', (_message.Message,), {
  'DESCRIPTOR' : _REPLY,
  '__module__' : 'display_pb2'
  # @@protoc_insertion_point(class_scope:display.Reply)
  })
_sym_db.RegisterMessage(Reply)



_LAUNCH = _descriptor.ServiceDescriptor(
  name='Launch',
  full_name='display.Launch',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=269,
  serialized_end=386,
  methods=[
  _descriptor.MethodDescriptor(
    name='Start',
    full_name='display.Launch.Start',
    index=0,
    containing_service=None,
    input_type=_LAUNCHREQUEST,
    output_type=_REPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Terminate',
    full_name='display.Launch.Terminate',
    index=1,
    containing_service=None,
    input_type=_TERMINATEREQUEST,
    output_type=_REPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_LAUNCH)

DESCRIPTOR.services_by_name['Launch'] = _LAUNCH

# @@protoc_insertion_point(module_scope)
