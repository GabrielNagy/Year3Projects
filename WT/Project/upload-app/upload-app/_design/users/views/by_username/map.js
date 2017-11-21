function (doc) {
  if(doc.username && doc.email && doc.date) {
    emit(doc.username, doc.password)
  }
}
