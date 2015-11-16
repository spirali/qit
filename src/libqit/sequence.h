#ifndef QIT_SEQUENCE_H

#include <vector>
#include <stdio.h>

namespace qit {

template <typename T> class SequenceIterator {
    public:
	typedef std::vector<typename T::value_type> value_type;
	SequenceIterator(T &iterator, size_t size)
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

    protected:
	std::vector<T> iterators;
	size_t size;
	bool inited;
};

template <typename T>
class SequenceGenerator {

	public:

		typedef std::vector<typename T::value_type> value_type;
		SequenceGenerator(T &generator, size_t size)
			: generator(generator), size(size) {
			}

		bool generate(value_type &out) {
			if (out.size() != size) {
				out.resize(size);
			}
			for (int i = 0; i < size; i++) {
				generator.generate(out[i]);
			}
		}

	protected:
		T generator;
		size_t size;
};

/*template<typename T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& value)
{
    os << "[";
    typename std::vector<T>::const_iterator i;
    i = value.begin();
    if (i != value.end()) {
	os << *i;
	i++;
    }

    for (; i != value.end(); i++) {
	os << "," << *i;
    }

    os << "]";
    return os;
}*/

template<typename T>
void write(FILE *out, const std::vector<T> &value)
{
    size_t size = value.size();
    fwrite(&size, sizeof(size_t), 1, out);
    typename std::vector<T>::const_iterator i;
    for (i = value.begin(); i != value.end(); i++) {
	    write(out, *i);
    }
}

}

#endif // QIT_SEQUENCE_H
