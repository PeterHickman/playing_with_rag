def list_files(collection):
    filenames = loaded_files(collection)

    if len(filenames) == 0:
        print("The database is empty")
        return

    size_a = 0
    for filename in filenames:
        if len(filename) > size_a:
            size_a = len(filename)

    print("{column_a: <{size_a}}  Chunks".format(column_a="Filename", size_a=size_a))
    print(f"{"-" * size_a}  ------")

    for filename in loaded_files(collection):
        results = collection.get(where={"filename": filename})
        print("{filename: <{size_a}}  {count:6d}".format(filename=filename, size_a=size_a, count=len(results['ids'])))


def delete_file(collection, filename):
    c = 0

    results = collection.get(where={"filename": filename})

    c += len(results['ids'])

    if c > 0:
        collection.delete(results['ids'])
        print(f"Deleted {c} chunks for {filename}")
    else:
        print(f"No chunks found! Is {filename} actually loaded")


def loaded_files(collection):
    l = []

    results = collection.get(include=["metadatas"])

    for x in results['metadatas']:
        filename = x['filename']

        if filename not in l:
            l.append(filename)

    l.sort()

    return l


