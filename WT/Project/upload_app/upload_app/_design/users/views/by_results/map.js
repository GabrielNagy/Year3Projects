function (doc) {
  if (doc.doc_type == "Entry" && doc.tested) {
  emit([doc.total, doc.failed, doc.language, doc.author], doc.problem);
  }
}
