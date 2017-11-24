function (doc) {
  if (doc.doc_type == "Entry" && doc.original_source) {
  emit(doc.author, doc.original_source);
  }
}
