function (doc) {
  if (doc.doc_type == "Entry" && doc.original) {
  emit(doc.author, doc.original);
  }
}
