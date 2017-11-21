function (doc) {
  if (doc.doc_type == "User" && doc.email) {
    emit(doc.email);
  }
}
