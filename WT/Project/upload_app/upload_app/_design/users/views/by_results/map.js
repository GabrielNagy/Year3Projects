function (doc) {
  if (doc.doc_type == "Entry" && doc.tested == 1) {
  emit([doc.problem, doc.total, doc.failed, doc.language, doc.author], 1);
  }
}
