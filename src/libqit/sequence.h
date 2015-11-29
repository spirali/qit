#ifndef QIT_SEQUENCE_H
#define QIT_SEQUENCE_H

#include <vector>
#include <stdio.h>
#include <assert.h>

namespace qit {

template <typename T> class SequenceIterator {
    public:
	typedef std::vector<typename T::value_type> value_type;
	SequenceIterator(const T &iterator, size_t size)
	    : size(size), inited(false) {
		for (size_t i = 0; i < size; i++) {
			iterators.push_back(iterator);
		}
	    }

	bool next(value_type &out) {
	    if (!inited) {
		out.resize(size);
		for (int i = 0; i < size; i++) {
		    if (!iterators[i].next(out[i])) {
			return false;
		    }
		}
		inited = true;
		return true;
	    }

	    for (int i = 0; i < size; i++) {
		if (iterators[i].next(out[i])) {
			return true;
		}
		iterators[i].reset();
		assert(iterators[i].next(out[i]));
	    }
	    return false;
	}

	void reset() {
	    inited = false;
	    typename std::vector<T>::iterator i;
	    for (i = iterators.begin(); i != iterators.end(); i++) {
		i->reset();
	    }
	}

    QIT_ITERATOR_WRITE_METHOD

    protected:
	std::vector<T> iterators;
	size_t size;
	bool inited;
};

}

#endif // QIT_SEQUENCE_H
