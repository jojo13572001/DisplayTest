# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: owt-server-p2p.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='owt-server-p2p.proto',
  package='owt_server_p2p',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x14owt-server-p2p.proto\x12\x0eowt_server_p2p\" \n\rLaunchRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"%\n\x10TerminateRequest\x12\x11\n\tterminate\x18\x01 \x01(\x08\"(\n\x05Reply\x12\x0e\n\x06result\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t2\x91\x01\n\x06Launch\x12?\n\x05Start\x12\x1d.owt_server_p2p.LaunchRequest\x1a\x15.owt_server_p2p.Reply\"\x00\x12\x46\n\tTerminate\x12 .owt_server_p2p.TerminateRequest\x1a\x15.owt_server_p2p.Reply\"\x00\x62\x06proto3'
)




_LAUNCHREQUEST = _descriptor.Descriptor(
  name='LaunchRequest',
  full_name='owt_server_p2p.LaunchRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='owt_server_p2p.LaunchRequest.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=40,
  serialized_end=72,
)


_TERMINATEREQUEST = _descriptor.Descriptor(
  name='TerminateRequest',
  full_name='owt_server_p2p.TerminateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='terminate', full_name='owt_server_p2p.TerminateRequest.terminate', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_start=74,
  serialized_end=111,
)


_REPLY = _descriptor.Descriptor(
  name='Reply',
  full_name='owt_server_p2p.Reply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='owt_server_p2p.Reply.result', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message', full_name='owt_server_p2p.Reply.message', index=1,
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
  serialized_start=113,
  serialized_end=153,
)

DESCRIPTOR.message_types_by_name['LaunchRequest'] = _LAUNCHREQUEST
DESCRIPTOR.message_types_by_name['TerminateRequest'] = _TERMINATEREQUEST
DESCRIPTOR.message_types_by_name['Reply'] = _REPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LaunchRequest = _reflection.GeneratedProtocolMessageType('LaunchRequest', (_message.Message,), {
  'DESCRIPTOR' : _LAUNCHREQUEST,
  '__module__' : 'owt_server_p2p_pb2'
  # @@protoc_insertion_point(class_scope:owt_server_p2p.LaunchRequest)
  })
_sym_db.RegisterMessage(LaunchRequest)

TerminateRequest = _reflection.GeneratedProtocolMessageType('TerminateRequest', (_message.Message,), {
  'DESCRIPTOR' : _TERMINATEREQUEST,
  '__module__' : 'owt_server_p2p_pb2'
  # @@protoc_insertion_point(class_scope:owt_server_p2p.TerminateRequest)
  })
_sym_db.RegisterMessage(TerminateRequest)

Reply = _reflection.GeneratedProtocolMessageType('Reply', (_message.Message,), {
  'DESCRIPTOR' : _REPLY,
  '__module__' : 'owt_server_p2p_pb2'
  # @@protoc_insertion_point(class_scope:owt_server_p2p.Reply)
  })
_sym_db.RegisterMessage(Reply)



_LAUNCH = _descriptor.ServiceDescriptor(
  name='Launch',
  full_name='owt_server_p2p.Launch',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=156,
  serialized_end=301,
  methods=[
  _descriptor.MethodDescriptor(
    name='Start',
    full_name='owt_server_p2p.Launch.Start',
    index=0,
    containing_service=None,
    input_type=_LAUNCHREQUEST,
    output_type=_REPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='Terminate',
    full_name='owt_server_p2p.Launch.Terminate',
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