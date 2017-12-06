function (doc) {
  if (doc.doc_type == "Entry" && doc.tested) {
  emit([doc.problem, doc.total, doc.failed, doc.language, doc.author], 1);
  }
}
