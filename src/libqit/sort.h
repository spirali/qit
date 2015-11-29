#ifndef QIT_SORT_H

#include <vector>
#include <algorithm>

namespace qit {

template <typename T>
class SortIterator {
    public:
	typedef typename T::value_type value_type;
	SortIterator() : index(0) {}
	SortIterator(const T &iterator) {
		value_type value;
		T i(iterator);
		while (i.next(value)) {
			vector.push_back(value);
		}
		index = 0;
		std::sort(vector.begin(), vector.end());
	}
	
	bool next(value_type &out) {
		if (index >= vector.size()) {
		    return false;
		}
		out = vector[index];
		index++;
		return true;
	}

	void reset() {
		index = 0;
	}

	QIT_ITERATOR_WRITE_METHOD

    protected:
    typename std::vector<value_type> vector;
    int index;
};

}

#endif // QIT_RANGE_H
